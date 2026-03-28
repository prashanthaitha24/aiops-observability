# AIOps Observability

AI-powered anomaly detection for distributed systems running on Kubernetes, using Prometheus telemetry, Python-based feature extraction, and deep learning models for real-time anomaly scoring.

Runs locally on Mac using **kind + helm**.

## Overview

This project demonstrates an AIOps pipeline that collects live telemetry from a Kubernetes-hosted microservices application, transforms selected metrics into a feature vector, and runs anomaly detection models against that data in near real time.

The platform currently supports:

- A baseline threshold-based anomaly detector
- An MLP autoencoder for point-in-time anomaly detection
- An LSTM autoencoder for sequence-based anomaly detection

The detector exports its own anomaly metrics through a Prometheus-compatible `/metrics` endpoint, so the results can be inspected directly or visualized through Grafana.

## Technologies Used

- Python
- Kubernetes (kind)
- kubectl
- Helm
- Prometheus
- Grafana
- OpenTelemetry demo microservices
- TensorFlow
- scikit-learn
- joblib
- Prometheus Python client
- requests
- Docker Desktop for Mac

## What the Project Does

At a high level, the project works like this:

1. Microservices run inside a local Kubernetes cluster created with `kind`
2. Prometheus scrapes service and infrastructure metrics
3. The detector queries Prometheus at a fixed polling interval
4. Raw metrics are converted into a structured feature dictionary
5. A selected model scores the live telemetry
6. The detector computes:
   - anomaly score
   - detected / not detected
   - reconstruction error for deep learning models
   - top contributing features
7. The detector exports those results on its own `/metrics` endpoint

## Feature Set Used for Detection

The current feature set includes the following telemetry signals:

- `frontend_rps`
- `ads_rps`
- `cart_add_latency_ms`
- `cart_get_latency_ms`
- `cart_add_p95_latency_ms`
- `cart_get_p95_latency_ms`

These are built in `app/feature_builder.py`.

## Deep Learning Models Implemented

### 1. MLP Autoencoder
The MLP autoencoder works on a single feature snapshot at a time.

How it works:
- Scale a single feature vector
- Reconstruct the same vector using the trained autoencoder
- Compute reconstruction error
- Compare the error against a threshold
- If error exceeds threshold, mark as anomalous

This model is good for:
- point anomalies
- sudden metric spikes
- simple real-time scoring

### 2. LSTM Autoencoder
The LSTM autoencoder works on a sequence of recent feature vectors.

How it works:
- Maintain a rolling sequence buffer
- Wait for the buffer to fill to the configured sequence length
- Scale the sequence
- Reconstruct the sequence using the trained LSTM autoencoder
- Compute sequence reconstruction error
- Compare error to threshold
- Mark as anomalous if threshold is exceeded

This model is better for:
- temporal anomalies
- gradual degradations
- sequence-aware changes in behavior

## Project Structure

```text
aiops-detector/
├── app/
│   ├── anomaly_model.py
│   ├── config.py
│   ├── dl_model.py
│   ├── feature_builder.py
│   ├── lstm_model.py
│   ├── main.py
│   ├── metrics_exporter.py
│   ├── model_registry.py
│   ├── prometheus_api_client.py
│   └── result_publisher.py
├── data/
│   └── telemetry_training_data.csv
├── models/
│   ├── threshold.json
│   ├── lstm_autoencoder.pkl
│   ├── lstm_scaler.pkl
│   ├── lstm_threshold.json
│   └── lstm_metadata.json
├── train/
│   ├── train_autoencoder.py
│   └── train_lstm_autoencoder.py
├── tests/
├── requirements.txt
├── bootstrap_mac.sh
└── README.md
```

## Prerequisites

Before running the project, make sure you have the following installed:

- Docker Desktop
- Homebrew
- kind
- kubectl
- Helm
- Python
- Conda or virtual environment tooling

If you are on macOS, the repo provides a helper bootstrap script.

## Initial Setup After Cloning the Repo

### 1. Clone the repository

```bash
git clone <your-github-repo-url>
cd aiops-detector
```

### 2. Run the macOS bootstrap script

```bash
chmod +x bootstrap_mac.sh
./bootstrap_mac.sh
```

This script is expected to install or validate local dependencies needed for development on macOS.

### 3. Install Python dependencies

If you are using your base environment:

```bash
pip install -r requirements.txt
```

If you are using a dedicated deep learning conda environment:

```bash
conda create -n aiops-dl python=3.10 -y
conda activate aiops-dl
pip install -r requirements.txt
```

### 4. Verify important packages

```bash
python -c "import tensorflow as tf; print(tf.__version__)"
python -c "import prometheus_client, joblib, sklearn, requests; print('deps ok')"
```

## Start the Kubernetes Environment

### 1. Check Docker

```bash
docker ps
docker info >/dev/null && echo "docker ok"
```

### 2. Check kind clusters

```bash
kind get clusters
```

If your cluster already exists, you should see something like:

```text
aiops-demo
```

### 3. Check Kubernetes connectivity

```bash
kubectl cluster-info
kubectl get nodes
kubectl get ns
kubectl get pods -A
```

### 4. Check the application namespaces

```bash
kubectl get pods -n otel-demo
kubectl get pods -n aiops
kubectl get svc -n otel-demo
kubectl get svc -n aiops
```

You should confirm that at least these services and pods are available:

- `prometheus`
- `grafana`
- `frontend-proxy`
- `cart`
- `aiops-detector`

## If You Need to Deploy or Re-Deploy the Demo Stack

If the cluster is up but your demo stack is missing, first inspect Helm releases:

```bash
helm list -A
```

If your OpenTelemetry demo release exists, you can restart all deployments:

```bash
kubectl rollout restart deployment -n otel-demo --all
kubectl get pods -n otel-demo -w
```

If the stack is not deployed, use your Helm install command for the OpenTelemetry demo release.

## Port Forwarding Cheat Sheet

Open separate terminals for each of the following port-forwards and leave them running.

### Terminal 1 - Prometheus

```bash
kubectl -n otel-demo port-forward svc/prometheus 9090:9090
```

Expected local URL:
- http://127.0.0.1:9090

Health check:

```bash
curl -s http://127.0.0.1:9090/-/ready
curl -s "http://127.0.0.1:9090/api/v1/query?query=up"
```

### Terminal 2 - Grafana

```bash
kubectl -n otel-demo port-forward svc/grafana 3000:80
```

Expected local URL:
- http://127.0.0.1:3000

### Terminal 3 - Frontend

```bash
kubectl -n otel-demo port-forward svc/frontend-proxy 8080:8080
```

Expected local URL:
- http://127.0.0.1:8080

Quick check:

```bash
curl -I http://127.0.0.1:8080
```

### Terminal 4 - Cart Service

```bash
kubectl -n otel-demo port-forward svc/cart 8082:8080
```

Expected local URL:
- http://127.0.0.1:8082

Quick check:

```bash
curl -s http://127.0.0.1:8082/cart
```

## Running the Detector Locally

Open a new terminal.

### Option A - Baseline model

```bash
python -m app.main
```

### Option B - MLP Autoencoder

```bash
MODEL_MODE=dl DL_MODEL_TYPE=mlp_autoencoder python -m app.main
```

### Option C - LSTM Autoencoder

```bash
conda activate aiops-dl
MODEL_MODE=dl DL_MODEL_TYPE=lstm_autoencoder python -m app.main
```

The detector will:
- query Prometheus
- build features
- score them using the selected model
- export its own metrics on port `8001`

Detector metrics endpoint:

```bash
curl -s http://127.0.0.1:8001/metrics | grep aiops_dl
```

## Important Note About LSTM Warm-Up

The LSTM model requires a sequence buffer before it can score live data.

If:
- sequence length = `10`
- polling interval = `30 seconds`

then warm-up takes about:

- `10 x 30 = 300 seconds`
- approximately `5 minutes`

During warm-up, you may see log messages like:

```text
warming up sequence buffer: 1/10
warming up sequence buffer: 2/10
...
warming up sequence buffer: 10/10
```

That is expected behavior.

## Watching Detector Metrics Continuously

Open another terminal and run:

```bash
while true; do
  clear
  date
  curl -s http://127.0.0.1:8001/metrics | grep aiops_dl
  sleep 2
done
```

To stop the loop cleanly, use:

```bash
Ctrl+C
```

## Generating Demo Traffic

### Baseline traffic

```bash
while true; do
  curl -s http://127.0.0.1:8080 > /dev/null
  sleep 0.2
done
```

### Stronger cart anomaly load

```bash
while true; do
  for i in {1..200}; do
    curl -s http://127.0.0.1:8082/cart > /dev/null &
  done
  wait
  sleep 1
done
```

This is useful for validating anomaly detection behavior in both MLP and LSTM models.

## Expected Detector Behavior

For normal traffic, you may see:

```text
aiops_dl_anomaly_score 0.x
aiops_dl_anomaly_detected 0.0
```

For strong anomaly traffic, you should eventually see:

```text
aiops_dl_anomaly_score 1.0
aiops_dl_anomaly_detected 1.0
```

You may also see reconstruction error metrics such as:

```text
aiops_dl_reconstruction_error 3.31
```

## Model Training Commands

### Train the MLP Autoencoder

```bash
python train/train_autoencoder.py
```

### Train the LSTM Autoencoder

```bash
conda activate aiops-dl
python train/train_lstm_autoencoder.py
```

Expected outputs include model, scaler, threshold, and metadata artifacts under `models/`.

## Common Operational Commands

### Check cluster and workloads

```bash
kubectl get pods -A
kubectl get pods -n otel-demo
kubectl get pods -n aiops
kubectl get svc -n otel-demo
kubectl get svc -n aiops
```

### Check local ports

```bash
lsof -i :9090
lsof -i :3000
lsof -i :8080
lsof -i :8082
lsof -i :8001
```

### Kill a conflicting process

```bash
kill <PID>
```

If needed:

```bash
kill -9 <PID>
```

## Troubleshooting

### 1. `Address already in use`
A local port is already occupied.

Check:

```bash
lsof -i :9090
lsof -i :8001
```

Kill the conflicting process or change the port.

### 2. Prometheus timeout from detector
If you see timeouts to `127.0.0.1:9090`, your local Prometheus port-forward is not active.

Restart:

```bash
kubectl -n otel-demo port-forward svc/prometheus 9090:9090
```

### 3. LSTM model shows warm-up messages only
This is normal until the sequence buffer is full.

### 4. TensorFlow import issues
Use a compatible Python environment:

```bash
conda create -n aiops-dl python=3.10 -y
conda activate aiops-dl
pip install -r requirements.txt
```

### 5. Kubernetes pods disappeared after laptop sleep
Usually the pods still exist, but local port-forwards die. Re-run:
- Prometheus port-forward
- Grafana port-forward
- frontend port-forward
- cart port-forward
- local detector command
