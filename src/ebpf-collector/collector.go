package main

import (
	"bytes"
	"context"
	"crypto/tls"
	"crypto/x509"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"sync"
	"time"

	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promhttp"
)

var (
	eventsCollected = prometheus.NewCounterVec(
		prometheus.CounterOpts{
			Name: "ebpf_events_collected_total",
			Help: "Total number of eBPF syscall events captured by Tetragon collector",
		},
		[]string{"event_type"},
	)
	eventsExported = prometheus.NewCounterVec(
		prometheus.CounterOpts{
			Name: "ebpf_events_exported_total",
			Help: "Total number of eBPF events exported to ai-brain via mTLS OTel",
		},
		[]string{"event_type", "status"},
	)
)

func init() {
	prometheus.MustRegister(eventsCollected)
	prometheus.MustRegister(eventsExported)
}

// SyscallEvent represents a Tetragon eBPF exec or network event
type SyscallEvent struct {
	ID          string    `json:"id"`
	Timestamp   time.Time `json:"timestamp"`
	EventType   string    `json:"event_type"` // "exec" or "network"
	Namespace   string    `json:"namespace"`
	PodName     string    `json:"pod_name"`
	ContainerID string    `json:"container_id"`
	BinaryPath  string    `json:"binary_path"`
	CommandArgs []string  `json:"command_args"`
	SrcIP       string    `json:"src_ip,omitempty"`
	DstIP       string    `json:"dst_ip,omitempty"`
	DstPort     int       `json:"dst_port,omitempty"`
	Syscall     string    `json:"syscall"`
	PID         uint32    `json:"pid"`
	UID         uint32    `json:"uid"`
}

// CollectorConfig holds runtime configurations for the collector
type CollectorConfig struct {
	AIBrainURL string
	CertFile   string
	KeyFile    string
	CAFile     string
	HTTPClient *http.Client
}

// Collector captures eBPF events and streams them directly over mTLS without local stdout/file logs
type Collector struct {
	config CollectorConfig
	eventCh chan SyscallEvent
	mu      sync.RWMutex
	running bool
}

// NewCollector constructs an eBPF collector with mTLS configured client
func NewCollector(cfg CollectorConfig) *Collector {
	if cfg.HTTPClient == nil {
		cfg.HTTPClient = createMTLSClient(cfg.CertFile, cfg.KeyFile, cfg.CAFile)
	}
	return &Collector{
		config:  cfg,
		eventCh: make(chan SyscallEvent, 1000),
	}
}

func createMTLSClient(certFile, keyFile, caFile string) *http.Client {
	tlsConfig := &tls.Config{
		MinVersion: tls.VersionTLS13,
	}

	if certFile != "" && keyFile != "" {
		cert, err := tls.LoadX509KeyPair(certFile, keyFile)
		if err == nil {
			tlsConfig.Certificates = []tls.Certificate{cert}
		}
	}

	if caFile != "" {
		caCert, err := os.ReadFile(caFile)
		if err == nil {
			caCertPool := x509.NewCertPool()
			caCertPool.AppendCertsFromPEM(caCert)
			tlsConfig.RootCAs = caCertPool
		}
	} else {
		// Fallback for development/testing environment
		tlsConfig.InsecureSkipVerify = true
	}

	transport := &http.Transport{
		TLSClientConfig: tlsConfig,
	}

	return &http.Client{
		Transport: transport,
		Timeout:   10 * time.Second,
	}
}

// Start begins processing events from the channel
func (c *Collector) Start(ctx context.Context) {
	c.mu.Lock()
	c.running = true
	c.mu.Unlock()

	for {
		select {
		case <-ctx.Done():
			c.mu.Lock()
			c.running = false
			c.mu.Unlock()
			return
		case evt, ok := <-c.eventCh:
			if !ok {
				return
			}
			c.ExportEvent(ctx, evt)
		}
	}
}

// CaptureEvent enqueues a captured Tetragon eBPF syscall event
func (c *Collector) CaptureEvent(evt SyscallEvent) {
	eventsCollected.WithLabelValues(evt.EventType).Inc()
	select {
	case c.eventCh <- evt:
	default:
		// Channel full, drop to prevent backpressure blocking eBPF probe
	}
}

// ExportEvent sends event to ai-brain /ingest endpoint without local file/stdout logging
func (c *Collector) ExportEvent(ctx context.Context, evt SyscallEvent) error {
	payload, err := json.Marshal(evt)
	if err != nil {
		eventsExported.WithLabelValues(evt.EventType, "marshal_error").Inc()
		return err
	}

	req, err := http.NewRequestWithContext(ctx, http.MethodPost, c.config.AIBrainURL+"/ingest", bytes.NewBuffer(payload))
	if err != nil {
		eventsExported.WithLabelValues(evt.EventType, "request_creation_error").Inc()
		return err
	}
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("X-OTel-Source", "ebpf-collector")

	resp, err := c.config.HTTPClient.Do(req)
	if err != nil {
		eventsExported.WithLabelValues(evt.EventType, "network_error").Inc()
		return err
	}
	defer resp.Body.Close()
	io.Copy(io.Discard, resp.Body)

	if resp.StatusCode >= 200 && resp.StatusCode < 300 {
		eventsExported.WithLabelValues(evt.EventType, "success").Inc()
		return nil
	}

	eventsExported.WithLabelValues(evt.EventType, fmt.Sprintf("http_%d", resp.StatusCode)).Inc()
	return fmt.Errorf("unexpected status code: %d", resp.StatusCode)
}

func main() {
	aiBrainURL := os.Getenv("AI_BRAIN_URL")
	if aiBrainURL == "" {
		aiBrainURL = "http://localhost:8000"
	}

	collector := NewCollector(CollectorConfig{
		AIBrainURL: aiBrainURL,
		CertFile:   os.Getenv("MTLS_CERT_FILE"),
		KeyFile:    os.Getenv("MTLS_KEY_FILE"),
		CAFile:     os.Getenv("MTLS_CA_FILE"),
	})

	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	go collector.Start(ctx)

	// Expose metrics on port 8080
	http.Handle("/metrics", promhttp.Handler())
	http.HandleFunc("/healthz", func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
		w.Write([]byte("OK"))
	})

	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	// Run metrics HTTP server
	if err := http.ListenAndServe(":"+port, nil); err != nil {
		os.Exit(1)
	}
}
