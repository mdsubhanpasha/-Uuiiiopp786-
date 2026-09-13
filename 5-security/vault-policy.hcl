# WHY: Least-Privilege HashiCorp Vault RBAC Access Policy.
# WHAT: HCL Policy granting read access to pasha-q-omni secrets with 1-hour TTL.
# WHERE USED: 5-security Vault ACL role attachment.
# RECRUITER ANSWER: "Implements strict least-privilege Zero-Trust secret access policies in Vault."

path "secret/data/pasha-q-omni/*" {
  capabilities = ["read"]
}

path "sys/leases/renew" {
  capabilities = ["update"]
}
