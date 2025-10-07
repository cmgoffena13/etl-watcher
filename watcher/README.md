# Watcher Helm Chart

This Helm chart deploys the Watcher application to Kubernetes.

## Prerequisites

- Kubernetes 1.34+
- Helm 3.0+
- Docker Desktop with Kubernetes enabled (for local development)

## Installation

### 1. Start Dependencies (PostgreSQL + Redis)

```bash
# Start PostgreSQL and Redis via Docker Compose
docker-compose up -d postgres redis

# Verify they're running
docker ps
```

### 2. Build and Tag the Image

```bash
# Build the Watcher image
docker build -t watcher:latest .

# For Docker Desktop, the image will be available locally
```

### 3. Install the Chart

```bash
# Install with default values
helm install watcher ./watcher

# Or install with custom values
helm install watcher ./watcher --set replicaCount=3
```

### 4. Verify Installation

```bash
# Check pods
kubectl get pods

# Check services
kubectl get services

# Port forward to access the app
kubectl port-forward service/watcher 8000:80
```

Then visit http://localhost:8000

## Configuration

The chart supports the following configuration options in `values.yaml`:

### Database & Redis
- `watcher.database.url` - PostgreSQL connection string
- `watcher.redis.url` - Redis connection string

### Environment
- `watcher.envState` - Environment state (dev, test, prod)

### Optional Features
- `watcher.logfire.token` - Logfire monitoring token
- `watcher.slack.webhookUrl` - Slack webhook URL
- `watcher.autoCreateAnomalyDetectionRules` - Auto-create rules
- `watcher.profilingEnabled` - Enable profiling

## Development

For local development with Docker Desktop:

1. The chart uses `host.docker.internal` to connect to your docker-compose services
2. Make sure PostgreSQL and Redis are running via `docker-compose up -d postgres redis`
3. The app will connect to `host.docker.internal:5432` and `host.docker.internal:6379`
