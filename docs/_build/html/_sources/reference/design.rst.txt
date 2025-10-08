Design
=================

This section covers the design of Watcher. The concepts behind the design are:

- Configuration as Code
- Efficiency / Performance
- Scalability
- Reliability
- Observability

Configuration as Code
---------------------

Watcher is designed reflect configuration stored in source control. 
Any updates to the configuration in source control will be automatically reflected in Watcher. 
This ensures that the Watcher configuration stays synchronized with the configuration in your code.

It is recommended to store your Pipline configuration and Address Lineage in source control within your pipeline code.

Efficiency / Performance
------------------------

Watcher is designed to be efficient and performant to have a minimal impact on the data pipelines it is monitoring.
Any non-essential operations are designed to be ran in the background.

Scalability
-----------

Watcher is designed to be scalable and to be able to handle large amounts of data.
It can handle thousands of piplines and millions of executions through just one instance.

Reliability
-----------

Watcher is designed to be deployed on Kubernetes to allow for replicas and failover.

Observability
-------------

Watcher is designed to be observable through its integration with Logfire. 
Having an outside service monitoring the Watcher framework is essential for active monitoring.