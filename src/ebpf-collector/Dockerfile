FROM golang:1.22-alpine AS builder

WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o ebpf-collector main.go collector.go

FROM alpine:3.19 AS runner

WORKDIR /app
COPY --from=builder /app/ebpf-collector .

RUN addgroup -g 10003 appgroup && \
    adduser -u 10003 -G appgroup -D -s /bin/false appuser && \
    chown -R appuser:appgroup /app

USER 10003:10003

EXPOSE 8080
HEALTHCHECK --interval=10s --timeout=3s --retries=3 \
  CMD wget -qO- http://localhost:8080/healthz || exit 1

ENTRYPOINT ["./ebpf-collector"]
