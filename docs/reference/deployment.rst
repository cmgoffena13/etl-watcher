Kubernetes Deployment Guides
=============================

This guide covers deploying Watcher to Kubernetes using Helm charts. 
We'll walk through the complete process from prerequisites to a fully functional 
deployment.


Scaling
-------

Scale Application Pods
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   kubectl scale deployment watcher --replicas=3

Scale Celery Workers
~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   kubectl scale deployment watcher-celery --replicas=4


Advanced Configuration
----------------------

Custom Values
~~~~~~~~~~~~~

Create a custom values file for your environment:

.. code-block:: yaml

   # custom-values.yaml
   image:
     repository: "your-registry/watcher"
     tag: "v1.0.0"
   
   resources:
     requests:
       memory: "1Gi"
       cpu: "500m"
     limits:
       memory: "2Gi"
       cpu: "1000m"

Deploy with custom values:

.. code-block:: bash

   helm install watcher ./watcher -f custom-values.yaml

Multiple Environments
~~~~~~~~~~~~~~~~~~~~

Deploy to different environments:

.. code-block:: bash

   # Development
   helm install watcher-dev ./watcher -f values-dev.yaml

   # Staging  
   helm install watcher-staging ./watcher -f values-staging.yaml

   # Production
   helm install watcher-prod ./watcher -f values-prod.yaml

