# Mini Project Study Case 4 - DevOps

This mini project builds an observability stack to validate service performance and stability before launch. The main focus is to provide a target application that exposes metrics, then connect it to monitoring and load-testing components that other team members can use.

---

## Daftar Isi

1. [Purpose](#purpose)
2. [Anggota Kelompok](#anggota-kelompok)
3. [Gambaran Arsitektur](#gambaran-arsitektur)
   - [Diagram Arsitektur](#1-diagram-arsitektur)
   - [Alur Kerja Sistem](#2-alur-kerja-sistem)
4. [Spesifikasi VM](#spesifikasi-vm)
5. [Informasi Jaringan dan IP Address](#informasi-jaringan-dan-ip-address)
   - [Resource Azure](#resource-azure)
   - [IP Address](#ip-address)
   - [Port yang Digunakan](#port-yang-digunakan)
   - [Akses Service](#akses-service)
6. [Struktur Project](#struktur-project)
7. [Fitur yang Diimplementasikan](#fitur-yang-diimplementasikan)
   - [Infrastructure as Code dengan Terraform](#1-infrastructure-as-code-dengan-terraform)
   - [Configuration as Code dengan Ansible](#2-configuration-as-code-dengan-ansible)
   - [Application Monitoring](#3-application-monitoring)
   - [Infrastructure Monitoring](#4-infrastructure-monitoring)
   - [Grafana Dashboard](#5-grafana-dashboard)
   - [Alerting](#6-alerting)
   - [Load Testing](#7-load-testing)
8. [Prasyarat Setup Awal](#prasyarat-setup-awal)
   - [Tools yang Dibutuhkan](#1-tools-yang-dibutuhkan)
   - [Login Azure](#2-login-azure)
   - [Setup SSH Key](#3-setup-ssh-key)
9. [Provisioning Infrastruktur dengan Terraform](#provisioning-infrastruktur-dengan-terraform)
10. [Tes Koneksi Ansible](#tes-koneksi-ansible)
11. [Install Dependencies dengan Ansible](#install-dependencies-dengan-ansible)
12. [Deploy Aplikasi](#deploy-aplikasi)
13. [Deploy Monitoring Stack](#deploy-monitoring-stack)
14. [Akses Grafana](#akses-grafana)
15. [Akses Prometheus dan Alertmanager](#akses-prometheus-dan-alertmanager)
16. [Validasi Endpoint Aplikasi](#validasi-endpoint-aplikasi)
17. [Validasi Prometheus Target](#validasi-prometheus-target)
18. [Alerting Rules dan Alertmanager](#alerting-rules-dan-alertmanager)
19. [Load Testing Menggunakan k6](#load-testing-menggunakan-k6)
20. [Dashboard Grafana](#dashboard-grafana)
21. [Testing Error Rate dan Alert](#testing-error-rate-dan-alert)
22. [Docker Security Scan](#docker-security-scan)
23. [Bukti Screenshot yang Perlu Disiapkan](#bukti-screenshot-yang-perlu-disiapkan)
24. [Troubleshooting](#troubleshooting)
25. [Cleanup Resource](#cleanup-resource)

---

## Purpose

The goal of this project is to provide an end-to-end workflow for:

- running a FastAPI application as the traffic target and metrics source,
- exposing Prometheus metrics from the application,
- preparing a monitoring stack such as Prometheus, Alertmanager, and Grafana,
- running k6 load tests to evaluate latency and error rate,
- monitoring VM infrastructure metrics using Node Exporter,
- supporting a clean handoff between project roles in the DevOps team.

---

## Anggota Kelompok

| No | Nama | NRP |
|---:|---|---|
| 1 | MUHAMMAD IDA BAGUS RAFI HABIBIE | 5027221059 |
| 2 | SALSABILA RAHMAH | 5027231005 |
| 3 | HAZWAN ADHIKARA NASUTION | 5027231017 |
| 4 | TSALDIA HUKMA CITA | 5027231036 |
| 5 | RANDIST PRAWANDHA PUTERA | 5027231059 |
| 6 | HASAN | 5027231073 |
| 7 | NABIEL NIZAR ANWARI | 5027231087 |

---

## Gambaran Arsitektur

### 1. Diagram Arsitektur

```text
+-------------------------------------------------------------+
|                         Local / WSL                         |
|-------------------------------------------------------------|
|                                                             |
|  Terraform CLI                                              |
|  Ansible CLI                                                |
|  k6 Load Generator                                          |
|                                                             |
|  k6 traffic:                                                |
|  http://4.193.183.63:3000/api/users                         |
|  http://4.193.183.63:3000/api/products                      |
|                                                             |
+----------------------------+--------------------------------+
                             |
                             | SSH / HTTP
                             |
                             v
+-------------------------------------------------------------+
|                       Azure Cloud                           |
|-------------------------------------------------------------|
|                                                             |
|  Resource Group: rg-observability-project-2                 |
|                                                             |
|  +----------------------------+   Private Network            |
|  |      Application VM        |<-------------------------+   |
|  |----------------------------|                          |   |
|  | Public IP : 4.193.183.63   |                          |   |
|  | Private IP: 10.0.1.4       |                          |   |
|  |                            |                          |   |
|  | Docker Containers:         |                          |   |
|  | - fastapi-app              |                          |   |
|  | - node-exporter            |                          |   |
|  |                            |                          |   |
|  | Ports:                     |                          |   |
|  | - 3000: FastAPI App        |                          |   |
|  | - 9100: Node Exporter      |                          |   |
|  +----------------------------+                          |   |
|                                                        scrape |
|                                                           |   |
|  +----------------------------+                          |   |
|  |       Monitoring VM        |--------------------------+   |
|  |----------------------------|                              |
|  | Public IP : 104.43.108.63  |                              |
|  | Private IP: 10.0.1.5       |                              |
|  |                            |                              |
|  | Docker Containers:         |                              |
|  | - prometheus               |                              |
|  | - alertmanager             |                              |
|  | - grafana                  |                              |
|  | - node-exporter-monitoring |                              |
|  |                            |                              |
|  | Ports:                     |                              |
|  | - 9090: Prometheus         |                              |
|  | - 9093: Alertmanager       |                              |
|  | - 3000: Grafana            |                              |
|  | - 9100: Node Exporter      |                              |
|  +----------------------------+                              |
|                                                             |
+-------------------------------------------------------------+
```

### 2. Alur Kerja Sistem

```text
1. Terraform membuat resource Azure:
   - Resource Group
   - Virtual Network
   - Subnet
   - Network Security Group
   - Public IP
   - Network Interface
   - Application VM
   - Monitoring VM

2. Ansible menginstall dependency:
   - Docker Engine
   - Docker Compose plugin
   - UFW rule
   - Package dependency

3. Ansible deploy aplikasi:
   - Copy source aplikasi ke Application VM
   - Build Docker image FastAPI
   - Run container fastapi-app
   - Run container node-exporter

4. Ansible deploy monitoring:
   - Copy prometheus.yml
   - Copy alerting-rules.yml
   - Copy alertmanager.yml
   - Copy Grafana provisioning
   - Copy Grafana dashboard JSON
   - Generate docker-compose.yml
   - Run Prometheus, Alertmanager, Grafana, Node Exporter Monitoring

5. Prometheus scrape metrics:
   - App metrics dari 10.0.1.4:3000/metrics
   - Node Exporter App VM dari 10.0.1.4:9100/metrics
   - Node Exporter Monitoring VM dari 10.0.1.5:9100/metrics
   - Prometheus self metrics dari localhost:9090
   - Alertmanager metrics dari alertmanager:9093

6. Grafana membaca datasource Prometheus:
   - Menampilkan request rate
   - Menampilkan latency
   - Menampilkan error rate
   - Menampilkan CPU/RAM/Disk/Network per VM
   - Menampilkan alert status
   - Menampilkan dampak k6 load testing

7. k6 dijalankan dari WSL/local:
   - Mengirim traffic ke Application VM public IP
   - Metrik traffic terekam oleh aplikasi
   - Prometheus scrape metrik aplikasi
   - Grafana menampilkan grafik load test
```

---

## Spesifikasi VM

| VM | OS | Fungsi | Service Utama |
|---|---|---|---|
| Application VM | Ubuntu 22.04 LTS | Menjalankan aplikasi API | FastAPI App, Node Exporter |
| Monitoring VM | Ubuntu 22.04 LTS | Menjalankan monitoring stack | Prometheus, Grafana, Alertmanager, Node Exporter |

> Spesifikasi ukuran VM mengikuti konfigurasi Terraform yang digunakan pada file `terraform/main.tf` atau variabel Terraform. Sesuaikan bagian ini jika ukuran VM berubah.

| Komponen | Application VM | Monitoring VM |
|---|---|---|
| OS | Ubuntu 22.04 LTS | Ubuntu 22.04 LTS |
| Username | azureuser | azureuser |
| Authentication | SSH Key | SSH Key |
| Private IP | 10.0.1.4 | 10.0.1.5 |
| Public IP | 4.193.183.63 | 104.43.108.63 |
| App Port | 3000 | - |
| Prometheus Port | - | 9090 |
| Alertmanager Port | - | 9093 |
| Grafana Port | - | 3000 |
| Node Exporter Port | 9100 | 9100 |

---

## Informasi Jaringan dan IP Address

### Resource Azure

| Resource | Nama |
|---|---|
| Resource Group | `rg-observability-project-2` |
| Location | `Southeast Asia` |
| Virtual Network | `vnet-observability` |
| Network Security Group | `nsg-observability` |
| Application Public IP | `pip-app-node` |
| Monitoring Public IP | `pip-mon-node` |

### IP Address

| Node | Public IP | Private IP |
|---|---:|---:|
| Application VM | `4.193.183.63` | `10.0.1.4` |
| Monitoring VM | `104.43.108.63` | `10.0.1.5` |

### Port yang Digunakan

| Port | Service | Node | Akses |
|---:|---|---|---|
| 22 | SSH | App dan Monitoring | Public, dibatasi NSG/UFW |
| 3000 | FastAPI App | Application VM | Public |
| 3000 | Grafana | Monitoring VM | Public |
| 9090 | Prometheus | Monitoring VM | Internal / SSH Tunnel |
| 9093 | Alertmanager | Monitoring VM | Internal / SSH Tunnel |
| 9100 | Node Exporter | App dan Monitoring | Internal scraping |

### Akses Service

| Service | URL |
|---|---|
| App Health | `http://4.193.183.63:3000/health` |
| App Metrics | `http://4.193.183.63:3000/metrics` |
| API Users | `http://4.193.183.63:3000/api/users` |
| API Products | `http://4.193.183.63:3000/api/products` |
| Grafana | `http://104.43.108.63:3000` |
| Prometheus via SSH Tunnel | `http://localhost:9090` |
| Alertmanager via SSH Tunnel | `http://localhost:9093` |

---

## Struktur Project

```text
devops-group6/
├── app/
│   ├── Dockerfile
│   └── src/
│       ├── main.py
│       ├── metrics.py
│       └── routes/
│           ├── health.py
│           ├── products.py
│           └── users.py
│
├── terraform/
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   ├── terraform.tfvars
│   └── providers.tf
│
├── ansible/
│   ├── inventory.ini
│   ├── files/
│   │   ├── prometheus.yml
│   │   ├── alerting-rules.yml
│   │   ├── alertmanager.yml
│   │   └── grafana/
│   │       ├── provisioning/
│   │       │   ├── datasources/
│   │       │   │   └── prometheus-datasource.yml
│   │       │   └── dashboards/
│   │       │       └── dashboard-provider.yml
│   │       └── dashboards/
│   │           └── observability-dashboard.json
│   └── playbooks/
│       ├── dependencies.yml
│       ├── app-deploy.yml
│       └── monitoring.yml
│
├── K6/
│   └── load-test.js
│
└── README.md
```

---

## Fitur yang Diimplementasikan

### 1. Infrastructure as Code dengan Terraform

- Membuat resource group Azure.
- Membuat virtual network.
- Membuat subnet.
- Membuat NSG.
- Membuat public IP untuk App VM dan Monitoring VM.
- Membuat network interface.
- Membuat Application VM.
- Membuat Monitoring VM.
- Mengatur SSH key untuk login VM.

### 2. Configuration as Code dengan Ansible

- Install Docker di kedua VM.
- Install package dependency.
- Mengatur firewall/UFW.
- Deploy aplikasi FastAPI.
- Deploy Node Exporter di Application VM.
- Deploy Prometheus, Grafana, Alertmanager di Monitoring VM.
- Deploy Node Exporter di Monitoring VM.
- Copy konfigurasi Prometheus, Alertmanager, Grafana.
- Generate Docker Compose monitoring stack.
- Validasi service dan target Prometheus.

### 3. Application Monitoring

- Endpoint `/health`.
- Endpoint `/metrics`.
- Endpoint `/api/users`.
- Endpoint `/api/products`.
- Endpoint `/api/error` untuk testing error rate.
- Custom metrics:
  - HTTP request total
  - HTTP request duration
  - HTTP request in progress

### 4. Infrastructure Monitoring

- CPU usage per VM.
- Memory/RAM usage per VM.
- Disk usage per VM.
- Network receive/transmit per VM.
- Node Exporter untuk App VM.
- Node Exporter untuk Monitoring VM.

### 5. Grafana Dashboard

Dashboard otomatis diprovision dari JSON dan menampilkan:

- Application Target Status
- Node Exporter Target Status
- Active Alerts
- Firing Alerts
- HTTP Request Rate
- P95 Latency
- Error Rate
- Requests In Progress
- CPU Usage by VM
- RAM / Memory Usage by VM
- Disk Usage by VM
- Network Receive / Transmit
- k6 Impact - App Request Rate
- k6 Impact - API P95 Latency
- k6 Impact - API Error Rate
- Alerts by Severity
- Active Alert Details
- Alert Status Timeline
- Prometheus Alert Rules Status

### 6. Alerting

Alert rules yang digunakan:

- HighRequestLatency
- CriticalRequestLatency
- HighErrorRate
- CriticalErrorRate
- ServiceDown
- ScrapeFailed
- LowDiskSpace
- CriticalDiskSpace
- HighCPUUsage
- CriticalCPUUsage
- LowMemoryAvailable
- CriticalMemoryUsage

Severity yang digunakan:

- `warning`
- `critical`

### 7. Load Testing

Load testing menggunakan k6 dengan target:

- 1.000 virtual users
- Durasi total 5 menit
- Threshold p95 latency < 200 ms
- Threshold error rate < 5%

---

## Prasyarat Setup Awal

Jalankan project dari WSL atau Linux environment.

### 1. Tools yang Dibutuhkan

Pastikan tools berikut tersedia:

```bash
az --version
terraform version
ansible --version
docker --version
k6 version
```

### 2. Login Azure

```bash
az login
az account show
```

Pastikan subscription yang aktif sudah benar.

Contoh output:

```text
Name                User
------------------  ----------------------------
Azure for Students  5027231036@student.its.ac.id
```

### 3. Setup SSH Key

Cek apakah SSH key sudah tersedia:

```bash
ls -la ~/.ssh/id_rsa_azure
ls -la ~/.ssh/id_rsa_azure.pub
```

Jika belum ada, buat SSH key:

```bash
ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa_azure
```

---

## Provisioning Infrastruktur dengan Terraform

### 1. Masuk ke Folder Terraform

```bash
cd /mnt/d/kuliah/devops-group6/terraform
```

### 2. Cek File Variabel

Pastikan `terraform.tfvars` berisi konfigurasi yang benar.

Contoh:

```hcl
my_ip                = "YOUR_PUBLIC_IP/32"
ssh_public_key_path  = "/home/tsaldia/.ssh/id_rsa_azure.pub"
location             = "Southeast Asia"
resource_group_name  = "rg-observability-project-2"
```

Cek IP publik lokal:

```bash
curl ifconfig.me
```

Masukkan hasilnya ke `my_ip` dengan format `/32`.

### 3. Terraform Init

```bash
terraform init
```

### 4. Terraform Plan

```bash
terraform plan
```

Pastikan tidak ada error.

### 5. Terraform Apply

```bash
terraform apply
```

Ketik:

```text
yes
```

### 6. Cek Resource Azure

```bash
az resource list \
  --resource-group rg-observability-project-2 \
  --output table
```

### 7. Cek Public IP

```bash
az network public-ip list \
  --resource-group rg-observability-project-2 \
  --query "[].{Name:name, IP:ipAddress}" \
  --output table
```

Output:

```text
Name          IP
------------  -------------
pip-app-node  4.193.183.63
pip-mon-node  104.43.108.63
```

### 8. Tes SSH ke VM

Application VM:

```bash
ssh -i /home/tsaldia/.ssh/id_rsa_azure azureuser@4.193.183.63
hostname
exit
```

Monitoring VM:

```bash
ssh -i /home/tsaldia/.ssh/id_rsa_azure azureuser@104.43.108.63
hostname
exit
```

---

## Tes Koneksi Ansible

Jalankan dari root project:

```bash
cd /mnt/d/kuliah/devops-group6
ansible -i ansible/inventory.ini all -m ping
```

Output yang diharapkan:

```text
app | SUCCESS => {
    "changed": false,
    "ping": "pong"
}

monitoring | SUCCESS => {
    "changed": false,
    "ping": "pong"
}
```

---

## Install Dependencies dengan Ansible

Playbook:

```text
ansible/playbooks/dependencies.yml
```

Fungsi playbook:

- Update apt cache.
- Install prerequisite package.
- Menambahkan Docker GPG key.
- Menambahkan Docker repository.
- Install Docker Engine.
- Install Docker Compose plugin.
- Start dan enable Docker.
- Menambahkan user SSH ke group Docker.
- Mengatur UFW firewall.

Jalankan:

```bash
ansible-playbook -i ansible/inventory.ini ansible/playbooks/dependencies.yml
```

Cek Docker di semua VM:

```bash
ansible -i ansible/inventory.ini all -m shell -a "docker --version"
```

Output yang diharapkan:

```text
app | CHANGED | rc=0 >>
Docker version ...

monitoring | CHANGED | rc=0 >>
Docker version ...
```

---

## Deploy Aplikasi

Aplikasi dijalankan di Application VM menggunakan Docker container.

Playbook:

```text
ansible/playbooks/app-deploy.yml
```

### 1. Fungsi `app-deploy.yml`

Playbook ini melakukan:

```text
1. Copy source aplikasi ke Application VM
2. Build Docker image fastapi-app:latest
3. Stop container lama jika ada
4. Remove container lama jika ada
5. Run container fastapi-app
6. Validasi container running
7. Validasi endpoint /health
8. Validasi endpoint /metrics
9. Deploy Node Exporter container
10. Validasi Node Exporter
```

### 2. Deploy Semua Aplikasi

```bash
ansible-playbook -i ansible/inventory.ini ansible/playbooks/app-deploy.yml
```

### 3. Deploy Hanya Node Exporter

Jika hanya ingin menjalankan task Node Exporter:

```bash
ansible-playbook -i ansible/inventory.ini ansible/playbooks/app-deploy.yml --tags node-exporter
```

### 4. Cek Container Application VM

```bash
ssh -i /home/tsaldia/.ssh/id_rsa_azure azureuser@4.193.183.63
docker ps
exit
```

Container yang diharapkan:

```text
fastapi-app
node-exporter
```

### 5. Cek Endpoint Aplikasi

```bash
curl http://4.193.183.63:3000/health
curl -s http://4.193.183.63:3000/metrics | head
curl http://4.193.183.63:3000/api/users
curl http://4.193.183.63:3000/api/products
```

Expected `/health`:

```json
{"status":"ok","uptime":...}
```

---

## Deploy Monitoring Stack

Monitoring stack dijalankan di Monitoring VM.

Playbook:

```text
ansible/playbooks/monitoring.yml
```

### 1. Fungsi `monitoring.yml`

Playbook ini melakukan:

```text
1. Membersihkan duplicate Docker repository jika ada
2. Membuat direktori /opt/monitoring
3. Membuat direktori Prometheus
4. Membuat direktori Alertmanager
5. Membuat direktori Grafana
6. Verifikasi Docker
7. Membuka firewall port Prometheus, Alertmanager, Grafana
8. Copy prometheus.yml
9. Copy alerting-rules.yml
10. Validasi Prometheus config
11. Copy alertmanager.yml
12. Validasi Alertmanager config
13. Copy Grafana provisioning dan dashboard JSON
14. Generate docker-compose.yml
15. Pull Docker images
16. Run Prometheus, Alertmanager, Grafana, Node Exporter Monitoring
17. Validasi Prometheus
18. Validasi Alertmanager
19. Cek Prometheus targets
20. Membuat summary deployment
```

### 2. Deploy Semua Monitoring Stack

```bash
ansible-playbook -i ansible/inventory.ini ansible/playbooks/monitoring.yml
```

### 3. Deploy Hanya Grafana Provisioning

Jika hanya mengubah dashboard JSON atau datasource Grafana:

```bash
ansible-playbook -i ansible/inventory.ini ansible/playbooks/monitoring.yml --tags grafana
```

Lalu restart Grafana:

```bash
ssh -i /home/tsaldia/.ssh/id_rsa_azure azureuser@104.43.108.63
docker restart grafana
exit
```

### 4. Cek Container Monitoring VM

```bash
ssh -i /home/tsaldia/.ssh/id_rsa_azure azureuser@104.43.108.63
docker ps
exit
```

Container yang diharapkan:

```text
prometheus
alertmanager
grafana
node-exporter-monitoring
```

---

## Akses Grafana

Grafana dapat diakses langsung dari browser:

```text
http://104.43.108.63:3000
```

Credential admin:

```text
Username: admin
Password: admin
```

Anonymous access diaktifkan sehingga dashboard bisa dibuka tanpa login manual. Login admin tetap tersedia jika perlu melakukan edit dashboard.

Dashboard:

```text
DevOps Observability Dashboard
```

---

## Akses Prometheus dan Alertmanager

Prometheus dan Alertmanager lebih aman diakses melalui SSH tunnel.

Jalankan dari WSL/local:

```bash
ssh -i /home/tsaldia/.ssh/id_rsa_azure \
  -L 9090:localhost:9090 \
  -L 9093:localhost:9093 \
  azureuser@104.43.108.63
```

Biarkan terminal tunnel tetap terbuka.

Akses melalui browser:

```text
Prometheus Targets : http://localhost:9090/targets
Prometheus Alerts  : http://localhost:9090/alerts
Prometheus Query   : http://localhost:9090/graph
Alertmanager       : http://localhost:9093
```

> Catatan: Jika terminal SSH tunnel ditutup, akses `localhost:9090` dan `localhost:9093` dari browser tidak akan berjalan. Jalankan ulang tunnel jika diperlukan.

---

## Validasi Endpoint Aplikasi

### 1. Health Check

```bash
curl http://4.193.183.63:3000/health
```

Expected:

```json
{"status":"ok","uptime":...}
```

### 2. Metrics

```bash
curl -s http://4.193.183.63:3000/metrics | head
```

Expected:

```text
# HELP ...
# TYPE ...
```

### 3. API Users

```bash
curl http://4.193.183.63:3000/api/users
```

### 4. API Products

```bash
curl http://4.193.183.63:3000/api/products
```

### 5. Error Rate Testing Endpoint

Endpoint ini digunakan untuk testing error rate dan alert.

```bash
curl -i http://4.193.183.63:3000/api/error
```

Expected:

```text
HTTP/1.1 500 Internal Server Error
```

Body:

```json
{"message":"intentional error for testing"}
```

---

## Validasi Prometheus Target

Masuk ke Monitoring VM:

```bash
ssh -i /home/tsaldia/.ssh/id_rsa_azure azureuser@104.43.108.63
```

Cek Prometheus health:

```bash
curl http://localhost:9090/-/healthy
```

Expected:

```text
Prometheus Server is Healthy.
```

Cek target Prometheus:

```bash
curl -s http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | {job: .labels.job, instance: .labels.instance, vm_name: .labels.vm_name, vm_role: .labels.vm_role, health: .health}'
```

Expected target:

```json
{
  "job": "app",
  "instance": "10.0.1.4:3000",
  "vm_name": null,
  "vm_role": null,
  "health": "up"
}
{
  "job": "node_exporter",
  "instance": "10.0.1.4:9100",
  "vm_name": "vm-application",
  "vm_role": "application",
  "health": "up"
}
{
  "job": "node_exporter",
  "instance": "10.0.1.5:9100",
  "vm_name": "vm-monitoring",
  "vm_role": "monitoring",
  "health": "up"
}
{
  "job": "prometheus",
  "instance": "localhost:9090",
  "health": "up"
}
{
  "job": "alertmanager",
  "instance": "alertmanager:9093",
  "health": "up"
}
```

Keluar dari VM:

```bash
exit
```

---

## Alerting Rules dan Alertmanager

### 1. File Alert Rules

File rules:

```text
ansible/files/alerting-rules.yml
```

Prometheus memuat file ini melalui:

```yaml
rule_files:
  - '/etc/prometheus/alerting-rules.yml'
```

Rule groups:

```text
application_alerts
availability_alerts
disk_alerts
system_alerts
```

Contoh alert:

```text
HighRequestLatency
CriticalRequestLatency
HighErrorRate
CriticalErrorRate
ServiceDown
ScrapeFailed
LowDiskSpace
CriticalDiskSpace
HighCPUUsage
CriticalCPUUsage
LowMemoryAvailable
CriticalMemoryUsage
```

Severity:

```text
warning
critical
```

### 2. Cek Rules dari Prometheus

```bash
ssh -i /home/tsaldia/.ssh/id_rsa_azure azureuser@104.43.108.63

curl -s http://localhost:9090/api/v1/rules | jq '.data.groups[] | {group: .name, rules: [.rules[] | {name: .name, state: .state, severity: .labels.severity}]}'

exit
```

### 3. Cek Alert Aktif

```bash
ssh -i /home/tsaldia/.ssh/id_rsa_azure azureuser@104.43.108.63

curl -s http://localhost:9090/api/v1/alerts | jq '.data.alerts[] | {alertname: .labels.alertname, severity: .labels.severity, state: .state, instance: .labels.instance}'

exit
```

### 4. Cek Alertmanager

```bash
ssh -i /home/tsaldia/.ssh/id_rsa_azure azureuser@104.43.108.63

curl http://localhost:9093/-/healthy
curl -s http://localhost:9093/api/v2/status | jq
curl -s http://localhost:9093/api/v2/alerts | jq

exit
```

---

## Load Testing Menggunakan k6

Script k6:

```text
K6/load-test.js
```

### 1. Konfigurasi k6 Sesuai ETS

Target load test:

```text
1.000 Virtual Users
Durasi total 5 menit
p95 latency < 200 ms
error rate < 5%
```

Contoh konfigurasi `options`:

```js
export const options = {
    stages: [
        { duration: '1m', target: 500 },
        { duration: '3m', target: 1000 },
        { duration: '1m', target: 0 },
    ],
    thresholds: {
        http_req_duration: ['p(95)<200'],
        error_rate: ['rate<0.05'],
    },
};
```

### 2. Menjalankan k6

```bash
cd /mnt/d/kuliah/devops-group6
BASE_URL=http://4.193.183.63:3000 k6 run K6/load-test.js
```

### 3. Hal yang Harus Terlihat di Terminal k6

Output k6 harus menunjukkan:

```text
Up to 1000 looping VUs
5m0s
http_reqs
checks_succeeded
checks_failed
http_req_duration p(95)
thresholds
vus_max: 1000
```

### 4. Monitoring k6 di Grafana

Saat k6 berjalan, buka:

```text
http://104.43.108.63:3000
```

Set:

```text
Time range: Last 15 minutes
Refresh: 5s
```

Panel yang harus bergerak:

```text
HTTP Request Rate
P95 Latency
Requests In Progress
CPU Usage by VM
RAM / Memory Usage by VM
Network Receive / Transmit
k6 Impact - App Request Rate
k6 Impact - API P95 Latency
k6 Impact - API Error Rate
```

### 5. Cek dari Prometheus

```bash
ssh -i /home/tsaldia/.ssh/id_rsa_azure azureuser@104.43.108.63
```

Request rate:

```bash
curl -g -s 'http://localhost:9090/api/v1/query?query=sum(rate(http_requests_total{route=~"/api/users|/api/products"}[5m]))' | jq
```

P95 latency:

```bash
curl -g -s 'http://localhost:9090/api/v1/query?query=histogram_quantile(0.95,sum(rate(http_request_duration_seconds_bucket{route=~"/api/users|/api/products"}[5m])) by (le))' | jq
```

Keluar:

```bash
exit
```

---

## Dashboard Grafana

Dashboard Grafana diprovision otomatis melalui file:

```text
ansible/files/grafana/dashboards/observability-dashboard.json
```

Datasource Grafana:

```text
ansible/files/grafana/provisioning/datasources/prometheus-datasource.yml
```

Dashboard provider:

```text
ansible/files/grafana/provisioning/dashboards/dashboard-provider.yml
```

### 1. Panel Dashboard

Panel yang tersedia:

```text
Application Target
Node Exporter Target
Active Alerts
Firing Alerts
HTTP Request Rate
P95 Latency
Error Rate
Requests In Progress
CPU Usage by VM
RAM / Memory Usage by VM
Disk Usage by VM
Network Receive / Transmit
k6 Impact - App Request Rate
k6 Impact - API P95 Latency
k6 Impact - API Error Rate
Alerts by Severity
Active Alert Details
Alert Status Timeline
Prometheus Alert Rules Status
```

---

## Testing Error Rate dan Alert

### 1. Testing Error Rate

Endpoint `/api/error` mengembalikan HTTP 500.

```bash
curl -i http://4.193.183.63:3000/api/error
```

Expected:

```text
HTTP/1.1 500 Internal Server Error
```

Cek error rate dari Prometheus:

```bash
ssh -i /home/tsaldia/.ssh/id_rsa_azure azureuser@104.43.108.63

curl -g -s 'http://localhost:9090/api/v1/query?query=sum(rate(http_requests_total{status_code=~"5.."}[5m]))' | jq

exit
```

### 2. Testing App Down Alert

Matikan container app:

```bash
ssh -i /home/tsaldia/.ssh/id_rsa_azure azureuser@4.193.183.63
docker stop fastapi-app
exit
```

Cek target:

```bash
ssh -i /home/tsaldia/.ssh/id_rsa_azure azureuser@104.43.108.63
curl -s http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | {job: .labels.job, instance: .labels.instance, health: .health}'
exit
```

Tunggu sesuai durasi `for:` pada alert rules. Alert akan muncul di:

```text
Prometheus /alerts
Alertmanager
Grafana Active Alerts
Grafana Alerts by Severity
Grafana Alert Status Timeline
```

Hidupkan kembali:

```bash
ssh -i /home/tsaldia/.ssh/id_rsa_azure azureuser@4.193.183.63
docker start fastapi-app
exit
```

### 3. Testing Node Exporter Down Alert

Matikan Node Exporter di Application VM:

```bash
ssh -i /home/tsaldia/.ssh/id_rsa_azure azureuser@4.193.183.63
docker stop node-exporter
exit
```

Cek target:

```bash
ssh -i /home/tsaldia/.ssh/id_rsa_azure azureuser@104.43.108.63
curl -s http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | {job: .labels.job, instance: .labels.instance, vm_name: .labels.vm_name, health: .health}'
exit
```

Hidupkan kembali:

```bash
ssh -i /home/tsaldia/.ssh/id_rsa_azure azureuser@4.193.183.63
docker start node-exporter
exit
```

---

## Dokumentasi Screenshot

Berikut adalah dokumentasi screenshot yang digunakan sebagai bukti implementasi **Mini Project Study Case 4 - DevOps**. Semua screenshot disimpan pada folder:

```text
screenshots/
```

Dokumentasi ini mencakup bukti provisioning infrastruktur Azure, konfigurasi VM, automasi Ansible, deployment aplikasi, deployment monitoring stack, validasi Prometheus, dashboard Grafana, dan load testing k6.

---

### 1. Provisioning Infrastruktur Azure

#### 1.1 Terraform Apply

Screenshot ini menunjukkan proses provisioning infrastruktur Azure menggunakan Terraform.

![Terraform Apply](screenshots/terraform.png)

#### 1.2 Azure Resource List

Screenshot ini menunjukkan resource Azure yang berhasil dibuat, seperti VM, Public IP, Network Interface, Virtual Network, dan Network Security Group.

![Azure Resource List](screenshots/azure-resource-list.png)

#### 1.3 Public IP List

Screenshot ini menunjukkan public IP dari Application VM dan Monitoring VM.

![Public IP List](screenshots/public-ip-list.png)

---

### 2. Validasi Akses VM

#### 2.1 SSH ke Application VM

Screenshot ini menunjukkan bahwa Application VM berhasil diakses melalui SSH dan memiliki private IP `10.0.1.4`.

![SSH Application VM](screenshots/ssh-app-vm.png)

#### 2.2 SSH ke Monitoring VM

Screenshot ini menunjukkan bahwa Monitoring VM berhasil diakses melalui SSH dan memiliki private IP `10.0.1.5`.

![SSH Monitoring VM](screenshots/ssh-monitoring-vm.png)

---

### 3. Validasi Ansible

#### 3.1 Ansible Ping

Screenshot ini menunjukkan bahwa Ansible berhasil terhubung ke dua VM, yaitu Application VM dan Monitoring VM.

![Ansible Ping](screenshots/ansible-ping.png)

#### 3.2 Install Dependencies dengan Ansible

Screenshot ini menunjukkan proses instalasi dependency menggunakan Ansible berhasil dijalankan.

![Ansible Dependencies](screenshots/ansible-dependencies.png)

#### 3.3 Docker Version di Semua VM

Screenshot ini menunjukkan Docker berhasil terinstall pada Application VM dan Monitoring VM.

![Docker Version All VM](screenshots/docker-version-all-vm.png)

---

### 4. Validasi Application Node

#### 4.1 Container di Application VM

Screenshot ini menunjukkan container `fastapi-app` dan `node-exporter` berjalan pada Application VM.

![Docker PS App VM](screenshots/docker-ps-app-vm.png)

#### 4.2 Endpoint Health

Screenshot ini menunjukkan endpoint `/health` berhasil diakses dan aplikasi berada dalam kondisi sehat.

![App Health](screenshots/app-health.png)

#### 4.3 Endpoint Metrics

Screenshot ini menunjukkan endpoint `/metrics` berhasil mengeluarkan metrik Prometheus dari aplikasi.

![App Metrics](screenshots/app-metrics.png)

#### 4.4 Endpoint API Users dan Products

Screenshot ini menunjukkan endpoint `/api/users` dan `/api/products` berhasil diakses.

![API Users Products](screenshots/api-users-products.png)

#### 4.5 Node Exporter Application VM

Screenshot ini menunjukkan Node Exporter pada Application VM berhasil mengeluarkan metrik infrastruktur.

![Node Exporter App](screenshots/node-exporter-app.png)

---

### 5. Validasi Monitoring Node

#### 5.1 Container di Monitoring VM

Screenshot ini menunjukkan container `prometheus`, `alertmanager`, `grafana`, dan `node-exporter-monitoring` berjalan pada Monitoring VM.

![Docker PS Monitoring VM](screenshots/docker-ps-monitoring-vm.png)

#### 5.2 Docker Compose Monitoring Stack

Screenshot ini menunjukkan service monitoring stack yang dijalankan menggunakan Docker Compose.

![Docker Compose Monitoring PS](screenshots/docker-compose-monitoring-ps.png)

#### 5.3 Node Exporter Monitoring VM

Screenshot ini menunjukkan Node Exporter pada Monitoring VM berhasil mengeluarkan metrik infrastruktur.

![Node Exporter Monitoring](screenshots/node-exporter-monitoring.png)

---

### 6. Validasi Service Monitoring

#### 6.1 Prometheus Health

Screenshot ini menunjukkan Prometheus berada dalam kondisi healthy dan ready.

![Prometheus Health](screenshots/prometheus-health.png)

#### 6.2 Grafana Health

Screenshot ini menunjukkan Grafana berhasil berjalan dan database Grafana dalam kondisi `ok`.

![Grafana Health](screenshots/grafana-health.png)

#### 6.3 Prometheus Targets dari Terminal

Screenshot ini menunjukkan target Prometheus dari terminal, termasuk `app`, `node_exporter`, `prometheus`, dan `alertmanager`.

![Prometheus Targets Terminal](screenshots/prometheus-targets-terminal.png)

#### 6.4 Prometheus Targets dari Web UI

Screenshot ini menunjukkan semua target Prometheus dalam kondisi `UP` melalui Web UI Prometheus.

![Prometheus Targets UI](screenshots/prometheus-targets-ui.png)

#### 6.5 Prometheus Alerts UI

Screenshot ini menunjukkan alert rules yang sudah terbaca oleh Prometheus.

![Prometheus Alerts UI](screenshots/prometheus-alerts-ui.png)

---

### 7. Validasi Grafana Dashboard

#### 7.1 Dashboard Overview

Screenshot ini menunjukkan dashboard utama Grafana yang berisi status target, request rate, latency, active alerts, dan firing alerts.

![Grafana Dashboard Overview](screenshots/grafana-dashboard-overview.png)

#### 7.2 VM Metrics Dashboard

Screenshot ini menunjukkan panel metrik infrastruktur VM, seperti CPU, RAM, disk, dan network usage.

![Grafana VM Metrics](screenshots/grafana-vm-metrics.png)

---

### 8. Validasi k6 Load Testing

#### 8.1 k6 Running 1000 VUs

Screenshot ini menunjukkan k6 dijalankan dengan skenario load test hingga 1.000 virtual users.

![k6 Running 1000 VUs](screenshots/k6-running-1000-vus.png)

---

## Troubleshooting

### 1. Prometheus `localhost:9090` Tidak Bisa Dibuka

Prometheus berjalan di Monitoring VM, bukan di laptop lokal. Untuk membuka Prometheus dari browser lokal, gunakan SSH tunnel:

```bash
ssh -i /home/tsaldia/.ssh/id_rsa_azure \
  -L 9090:localhost:9090 \
  -L 9093:localhost:9093 \
  azureuser@104.43.108.63
```

Setelah tunnel aktif, buka:

```text
http://localhost:9090/targets
http://localhost:9090/alerts
http://localhost:9093
```

### 2. Grafana Dashboard Tidak Berubah Setelah Edit JSON

Jalankan ulang provisioning Grafana:

```bash
ansible-playbook -i ansible/inventory.ini ansible/playbooks/monitoring.yml --tags grafana
```

Restart Grafana:

```bash
ssh -i /home/tsaldia/.ssh/id_rsa_azure azureuser@104.43.108.63
docker restart grafana
exit
```

Jika masih belum berubah, naikkan nilai `version` pada file:

```text
ansible/files/grafana/dashboards/observability-dashboard.json
```

Contoh:

```json
"version": 8
```

### 3. k6 Grafik Tidak Bergerak di Grafana

Cek route label di Prometheus:

```bash
ssh -i /home/tsaldia/.ssh/id_rsa_azure azureuser@104.43.108.63
curl -s "http://localhost:9090/api/v1/label/route/values" | jq
exit
```

Pastikan ada:

```text
/api/users
/api/products
```

Cek query request rate:

```bash
ssh -i /home/tsaldia/.ssh/id_rsa_azure azureuser@104.43.108.63
curl -g -s 'http://localhost:9090/api/v1/query?query=sum(rate(http_requests_total{route=~"/api/users|/api/products"}[5m]))' | jq
exit
```

### 4. Target Prometheus DOWN

Cek container di Application VM:

```bash
ssh -i /home/tsaldia/.ssh/id_rsa_azure azureuser@4.193.183.63
docker ps
exit
```

Cek container di Monitoring VM:

```bash
ssh -i /home/tsaldia/.ssh/id_rsa_azure azureuser@104.43.108.63
docker ps
exit
```

Restart container jika diperlukan:

```bash
docker restart fastapi-app
docker restart node-exporter
docker restart prometheus
docker restart grafana
docker restart alertmanager
docker restart node-exporter-monitoring
```

### 5. Error Docker Repository Signed-By Conflict

Jika muncul error:

```text
Conflicting values set for option Signed-By
```

Jalankan ulang playbook dependencies dan monitoring:

```bash
ansible-playbook -i ansible/inventory.ini ansible/playbooks/dependencies.yml
ansible-playbook -i ansible/inventory.ini ansible/playbooks/monitoring.yml
```

---

## Cleanup Resource

Jika project sudah selesai dan resource Azure ingin dihapus:

```bash
cd /mnt/d/kuliah/devops-group6/terraform
terraform destroy
```

Ketik:

```text
yes
```

Pastikan resource group dan subscription sudah benar sebelum menjalankan `terraform destroy`.

---