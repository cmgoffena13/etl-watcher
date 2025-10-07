Deployment Guide
=================

This section covers deployment strategies for Watcher. 
We'll be walking through a Kubernetes deployment of Watcher utilizing Helm charts.
You can test the deployment strategies utilizing Kubernetes in Docker Desktop.

Kubernetes
----------

Overview
~~~~~~~~

1. Install Docker Desktop
2. Install Kubernetes in Docker Desktop
3. Create a new Kubernetes cluster

Setup
~~~~~

1. Install Helm
2. Check Kubernetes







Namespace
~~~~~~~~~

.. code-block:: yaml

   apiVersion: v1
   kind: Namespace
   metadata:
     name: watcher


ConfigMap
~~~~~~~~~

.. code-block:: yaml

   apiVersion: v1
   kind: ConfigMap
   metadata:
     name: watcher-config
     namespace: watcher
   data:
     PROD_DATABASE_URL: "postgresql+asyncpg://user:password@your-db-host:5432/watcher"
     PROD_REDIS_URL: "redis://your-redis-host:6379/1"
     PROD_WATCHER_AUTO_CREATE_ANOMALY_DETECTION_RULES: "true"
     PROD_PROFILING_ENABLED: "false"

Secrets
~~~~~~~

.. code-block:: yaml

   apiVersion: v1
   kind: Secret
   metadata:
     name: watcher-secrets
     namespace: watcher
   type: Opaque
   data:
     PROD_LOGFIRE_TOKEN: <base64-encoded-token>
     PROD_SLACK_WEBHOOK_URL: <base64-encoded-webhook>

Watcher Application
~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: watcher-app
     namespace: watcher
   spec:
     replicas: 2
     selector:
       matchLabels:
         app: watcher-app
     template:
       metadata:
         labels:
           app: watcher-app
       spec:
         containers:
         - name: watcher
           image: watcher:latest
           ports:
           - containerPort: 8000
           envFrom:
           - configMapRef:
               name: watcher-config
           - secretRef:
               name: watcher-secrets
           livenessProbe:
             httpGet:
               path: /
               port: 8000
             initialDelaySeconds: 30
             periodSeconds: 10
           readinessProbe:
             httpGet:
               path: /
               port: 8000
             initialDelaySeconds: 5
             periodSeconds: 5
           resources:
             requests:
               memory: "512Mi"
               cpu: "250m"
             limits:
               memory: "1Gi"
               cpu: "500m"

   ---
   apiVersion: v1
   kind: Service
   metadata:
     name: watcher-service
     namespace: watcher
   spec:
     selector:
       app: watcher-app
     ports:
     - port: 80
       targetPort: 8000
     type: ClusterIP

Celery Workers
~~~~~~~~~~~~~~

.. code-block:: yaml

   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: watcher-celery
     namespace: watcher
   spec:
     replicas: 2
     selector:
       matchLabels:
         app: watcher-celery
     template:
       metadata:
         labels:
           app: watcher-celery
       spec:
         containers:
         - name: celery
           image: watcher:latest
           command: ["celery", "-A", "src.celery_app", "worker", "--loglevel=info"]
           envFrom:
           - configMapRef:
               name: watcher-config
           - secretRef:
               name: watcher-secrets
           resources:
             requests:
               memory: "256Mi"
               cpu: "100m"
             limits:
               memory: "512Mi"
               cpu: "250m"

