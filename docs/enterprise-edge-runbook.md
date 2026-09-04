# Enterprise Edge Delivery Fabric (NAYEEM-EDGE) Runbook

## 1. Executive System Architecture

The **NAYEEM-EDGE Enterprise Edge Delivery Fabric** serves as the initial edge ingress tier for the 30 Days Platform Engineering Challenge. It delivers zero-trust static assets with ultra-low latency, automated Let's Encrypt TLS renewal, Route53 global DNS routing, and enterprise security header hardening.

```
+------------------+         +----------------------+         +---------------------+
|   User / Client  | ------> |  Route53 DNS Record  | ------> |   AWS Elastic IP    |
|   (HTTPS Request)|         | (nayeem-edge.ent.io) |         |  (Static IPv4 EIP)  |
+------------------+         +----------------------+         +---------------------+
                                                                         |
                                                                         v
+------------------+         +----------------------+         +---------------------+
|  Let's Encrypt   | <-----> |   Certbot Renew      | <-----> |   EC2 Nginx Edge    |
|  TLS Authority   |         |   (Automated Cron)   |         | (Ubuntu 22.04 LTS)  |
+------------------+         +----------------------+         +---------------------+
                                                                         |
                                                                         v
                                                              +---------------------+
                                                              | Static Web Root &   |
                                                              | /health Telemetry   |
                                                              +---------------------+
```

---

## 2. Step-by-Step Deployment Guide

### Step 2.1: Terraform Infrastructure Provisioning
```bash
cd infrastructure/terraform-edge-fabric
terraform init
terraform plan
terraform apply -auto-approve
```

### Step 2.2: Ansible Nginx Hardening Playbook Execution
```bash
cd ../../ansible/enterprise-nginx-hardening-playbook
ansible-playbook -i inventory.ini nginx-setup.yml
```

### Step 2.3: Let's Encrypt SSL Provisioning & Auto-Renewal Setup
```bash
./scripts/ssl-automation/provision-letsencrypt.sh nayeem-edge.enterprise.io admin@enterprise.io
```

### Step 2.4: Domain & TLS Validation
```bash
./scripts/ssl-automation/validate-ssl.sh nayeem-edge.enterprise.io
```

### Step 2.5: Health Check & Security Header Verification
```bash
./scripts/validation/health-check.sh nayeem-edge.enterprise.io
```

### Step 2.6: Performance Benchmark Load Testing
```bash
./scripts/validation/performance-test.sh nayeem-edge.enterprise.io 1000 100
```

---

## 3. SLA & Operational Performance Metrics

| SLA Category | Metric Target | Production Standard |
| :--- | :--- | :--- |
| **Time to First Byte (TTFB)** | `< 100ms` | Edge cached static delivery |
| **SSL / TLS Rating** | `A+ Grade` | TLS 1.2/1.3, Let's Encrypt RSA 2048/ECC |
| **Security Header Compliance** | `100% (A+)` | HSTS, CSP, X-Frame DENY, X-Content nosniff |
| **Cache Efficiency** | `1 Year (Static)` | `Cache-Control: public, max-age=31536000` |
