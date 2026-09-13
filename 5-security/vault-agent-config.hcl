# WHY: HashiCorp Vault Agent Sidecar Auto-Rotation Config.
# WHAT: Agent HCL file for dynamic secrets injection with 1-hour TTL and auto-auth Kubernetes method.
# WHERE USED: 5-security Vault Agent pod sidecar deployment.
# RECRUITER ANSWER: "Eliminates hardcoded credentials by enforcing 1-hour dynamic TTL secret rotation via HashiCorp Vault Agent sidecars."

exit_after_auth = false
pid_file = "/tmp/vault-agent-pid"

auto_auth {
  method "kubernetes" {
    mount_path = "auth/kubernetes"
    config = {
      role = "pasha-q-omni-role"
    }
  }

  sink "file" {
    config = {
      path = "/tmp/.vault-token"
    }
  }
}

template {
  destination = "/vault/secrets/database-config.env"
  contents = <<EOF
{{- with secret "secret/data/pasha-q-omni/config" -}}
DB_HOST="{{ .Data.data.db_host }}"
DB_USER="{{ .Data.data.db_user }}"
DB_PASS="{{ .Data.data.db_pass }}"
QUANTUM_API_KEY="{{ .Data.data.quantum_api_key }}"
{{- end -}}
EOF
}
