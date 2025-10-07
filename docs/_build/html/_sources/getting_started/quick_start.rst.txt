Quick Start Guide
=================

This guide will get you up and running with Watcher.

Step 1: Create Your First Pipeline
----------------------------------

1. **Create a pipeline** (automatically creates pipeline type if needed)

   .. tabs::

      .. tab:: Python

         .. code-block:: python

            import httpx
            
            response = httpx.post("http://localhost:8000/pipeline", json={
                "name": "my data pipeline",
                "pipeline_type_name": "extraction"
            })
            print(response.json())

      .. tab:: curl

         .. code-block:: bash

            curl -X POST "http://localhost:8000/pipeline" \
                 -H "Content-Type: application/json" \
                 -d '{"name": "my data pipeline", "pipeline_type_name": "extraction"}'

      .. tab:: Go

         .. code-block:: go

            package main

            import (
                "bytes"
                "encoding/json"
                "fmt"
                "net/http"
            )

            type PipelineRequest struct {
                Name             string `json:"name"`
                PipelineTypeName string `json:"pipeline_type_name"`
            }

            func main() {
                data := PipelineRequest{
                    Name:             "my data pipeline",
                    PipelineTypeName: "extraction",
                }
                
                jsonData, _ := json.Marshal(data)
                resp, _ := http.Post("http://localhost:8000/pipeline", 
                    "application/json", bytes.NewBuffer(jsonData))
                defer resp.Body.Close()
                
                var result map[string]interface{}
                json.NewDecoder(resp.Body).Decode(&result)
                fmt.Println(result)
            }

      .. tab:: Scala

         .. code-block:: scala

            import scala.io.Source
            import java.net.http.{HttpClient, HttpRequest, HttpResponse}
            import java.net.URI
            import play.api.libs.json.Json

            object PipelineExample {
                def main(args: Array[String]): Unit = {
                    val client = HttpClient.newHttpClient()
                    
                    val json = Json.obj(
                        "name" -> "my data pipeline",
                        "pipeline_type_name" -> "extraction"
                    ).toString()
                    
                    val request = HttpRequest.newBuilder()
                        .uri(URI.create("http://localhost:8000/pipeline"))
                        .header("Content-Type", "application/json")
                        .POST(HttpRequest.BodyPublishers.ofString(json))
                        .build()
                    
                    val response = client.send(request, 
                        HttpResponse.BodyHandlers.ofString())
                    println(response.body())
                }
            }

Step 2: Start a Pipeline Execution
-------------------------------

2. **Start an execution**

   .. tabs::

      .. tab:: Python

         .. code-block:: python

            import httpx
            
            response = httpx.post("http://localhost:8000/start_pipeline_execution", json={
                "pipeline_id": 1,
                "start_date": "2024-01-01T10:00:00Z",
                "full_load": True
            })
            print(response.json())

      .. tab:: curl

         .. code-block:: bash

            curl -X POST "http://localhost:8000/start_pipeline_execution" \
                 -H "Content-Type: application/json" \
                 -d '{
                   "pipeline_id": 1,
                   "start_date": "2024-01-01T10:00:00Z",
                   "full_load": true
                 }'

      .. tab:: Go

         .. code-block:: go

            package main

            import (
                "bytes"
                "encoding/json"
                "fmt"
                "net/http"
            )

            type StartExecutionRequest struct {
                PipelineID int    `json:"pipeline_id"`
                StartDate  string `json:"start_date"`
                FullLoad   bool   `json:"full_load"`
            }

            func main() {
                data := StartExecutionRequest{
                    PipelineID: 1,
                    StartDate:  "2024-01-01T10:00:00Z",
                    FullLoad:   true,
                }
                
                jsonData, _ := json.Marshal(data)
                resp, _ := http.Post("http://localhost:8000/start_pipeline_execution", 
                    "application/json", bytes.NewBuffer(jsonData))
                defer resp.Body.Close()
                
                var result map[string]interface{}
                json.NewDecoder(resp.Body).Decode(&result)
                fmt.Println(result)
            }

      .. tab:: Scala

         .. code-block:: scala

            import java.net.http.{HttpClient, HttpRequest, HttpResponse}
            import java.net.URI
            import play.api.libs.json.Json

            object StartExecutionExample {
                def main(args: Array[String]): Unit = {
                    val client = HttpClient.newHttpClient()
                    
                    val json = Json.obj(
                        "pipeline_id" -> 1,
                        "start_date" -> "2024-01-01T10:00:00Z",
                        "full_load" -> true
                    ).toString()
                    
                    val request = HttpRequest.newBuilder()
                        .uri(URI.create("http://localhost:8000/start_pipeline_execution"))
                        .header("Content-Type", "application/json")
                        .POST(HttpRequest.BodyPublishers.ofString(json))
                        .build()
                    
                    val response = client.send(request, 
                        HttpResponse.BodyHandlers.ofString())
                    println(response.body())
                }
            }

3. **End the execution with metrics**

   .. tabs::

      .. tab:: Python

         .. code-block:: python

            import httpx
            
            response = httpx.post("http://localhost:8000/end_pipeline_execution", json={
                "id": 1,
                "pipeline_id": 1,
                "end_date": "2024-01-01T10:05:00Z",
                "completed_successfully": True,
                "total_rows": 1000,
                "inserts": 800,
                "updates": 200,
                "soft_deletes": 0
            })
            print(response.json())

      .. tab:: curl

         .. code-block:: bash

            curl -X POST "http://localhost:8000/end_pipeline_execution" \
                 -H "Content-Type: application/json" \
                 -d '{
                   "id": 1,
                   "pipeline_id": 1,
                   "end_date": "2024-01-01T10:05:00Z",
                   "completed_successfully": true,
                   "total_rows": 1000,
                   "inserts": 800,
                   "updates": 200,
                   "soft_deletes": 0
                 }'

      .. tab:: Go

         .. code-block:: go

            package main

            import (
                "bytes"
                "encoding/json"
                "fmt"
                "net/http"
            )

            type EndExecutionRequest struct {
                ID                   int  `json:"id"`
                PipelineID           int  `json:"pipeline_id"`
                EndDate              string `json:"end_date"`
                CompletedSuccessfully bool `json:"completed_successfully"`
                TotalRows            int  `json:"total_rows"`
                Inserts              int  `json:"inserts"`
                Updates              int  `json:"updates"`
                SoftDeletes          int  `json:"soft_deletes"`
            }

            func main() {
                data := EndExecutionRequest{
                    ID:                   1,
                    PipelineID:           1,
                    EndDate:              "2024-01-01T10:05:00Z",
                    CompletedSuccessfully: true,
                    TotalRows:            1000,
                    Inserts:              800,
                    Updates:              200,
                    SoftDeletes:          0,
                }
                
                jsonData, _ := json.Marshal(data)
                resp, _ := http.Post("http://localhost:8000/end_pipeline_execution", 
                    "application/json", bytes.NewBuffer(jsonData))
                defer resp.Body.Close()
                
                var result map[string]interface{}
                json.NewDecoder(resp.Body).Decode(&result)
                fmt.Println(result)
            }

      .. tab:: Scala

         .. code-block:: scala

            import java.net.http.{HttpClient, HttpRequest, HttpResponse}
            import java.net.URI
            import play.api.libs.json.Json

            object EndExecutionExample {
                def main(args: Array[String]): Unit = {
                    val client = HttpClient.newHttpClient()
                    
                    val json = Json.obj(
                        "id" -> 1,
                        "pipeline_id" -> 1,
                        "end_date" -> "2024-01-01T10:05:00Z",
                        "completed_successfully" -> true,
                        "total_rows" -> 1000,
                        "inserts" -> 800,
                        "updates" -> 200,
                        "soft_deletes" -> 0
                    ).toString()
                    
                    val request = HttpRequest.newBuilder()
                        .uri(URI.create("http://localhost:8000/end_pipeline_execution"))
                        .header("Content-Type", "application/json")
                        .POST(HttpRequest.BodyPublishers.ofString(json))
                        .build()
                    
                    val response = client.send(request, 
                        HttpResponse.BodyHandlers.ofString())
                    println(response.body())
                }
            }

Step 3: Create Address Lineage
----------------------------

1. **Create address lineage** (automatically creates addresses and address types if needed)

   .. tabs::

      .. tab:: Python

         .. code-block:: python

            import httpx
            
            response = httpx.post("http://localhost:8000/address_lineage", json={
                "pipeline_id": 1,
                "source_addresses": [
                    {
                        "name": "source_db.source_schema.source_table",
                        "address_type_name": "postgres",
                        "address_type_group_name": "database"
                    }
                ],
                "target_addresses": [
                    {
                        "name": "target_db.target_schema.target_table",
                        "address_type_name": "postgres",
                        "address_type_group_name": "database"
                    }
                ]
            })
            print(response.json())

      .. tab:: curl

         .. code-block:: bash

            curl -X POST "http://localhost:8000/address_lineage" \
                 -H "Content-Type: application/json" \
                 -d '{
                   "pipeline_id": 1,
                   "source_addresses": [
                     {
                       "name": "source_db.source_schema.source_table",
                       "address_type_name": "postgres",
                       "address_type_group_name": "database"
                     }
                   ],
                   "target_addresses": [
                     {
                       "name": "target_db.target_schema.target_table",
                       "address_type_name": "postgres",
                       "address_type_group_name": "database"
                     }
                   ]
                 }'

      .. tab:: Go

         .. code-block:: go

            package main

            import (
                "bytes"
                "encoding/json"
                "fmt"
                "net/http"
            )

            type AddressLineageRequest struct {
                PipelineID      int `json:"pipeline_id"`
                SourceAddresses []Address `json:"source_addresses"`
                TargetAddresses []Address `json:"target_addresses"`
            }

            type Address struct {
                Name                string `json:"name"`
                AddressTypeName     string `json:"address_type_name"`
                AddressTypeGroupName string `json:"address_type_group_name"`
            }

            func main() {
                data := AddressLineageRequest{
                    PipelineID: 1,
                    SourceAddresses: []Address{{
                        Name:                "source_db.source_schema.source_table",
                        AddressTypeName:     "postgres",
                        AddressTypeGroupName: "database",
                    }},
                    TargetAddresses: []Address{{
                        Name:                "target_db.target_schema.target_table",
                        AddressTypeName:     "postgres",
                        AddressTypeGroupName: "database",
                    }},
                }
                
                jsonData, _ := json.Marshal(data)
                resp, _ := http.Post("http://localhost:8000/address_lineage", 
                    "application/json", bytes.NewBuffer(jsonData))
                defer resp.Body.Close()
                
                var result map[string]interface{}
                json.NewDecoder(resp.Body).Decode(&result)
                fmt.Println(result)
            }

      .. tab:: Scala

         .. code-block:: scala

            import java.net.http.{HttpClient, HttpRequest, HttpResponse}
            import java.net.URI
            import play.api.libs.json.Json

            object AddressLineageExample {
                def main(args: Array[String]): Unit = {
                    val client = HttpClient.newHttpClient()
                    
                    val json = Json.obj(
                        "pipeline_id" -> 1,
                        "source_addresses" -> Json.arr(
                            Json.obj(
                                "name" -> "source_db.source_schema.source_table",
                                "address_type_name" -> "postgres",
                                "address_type_group_name" -> "database"
                            )
                        ),
                        "target_addresses" -> Json.arr(
                            Json.obj(
                                "name" -> "target_db.target_schema.target_table",
                                "address_type_name" -> "postgres",
                                "address_type_group_name" -> "database"
                            )
                        )
                    ).toString()
                    
                    val request = HttpRequest.newBuilder()
                        .uri(URI.create("http://localhost:8000/address_lineage"))
                        .header("Content-Type", "application/json")
                        .POST(HttpRequest.BodyPublishers.ofString(json))
                        .build()
                    
                    val response = client.send(request, 
                        HttpResponse.BodyHandlers.ofString())
                    println(response.body())
                }
            }

Step 4: Set Up Monitoring
--------------------------

1. **Run a freshness check**

   .. tabs::

      .. tab:: Python

         .. code-block:: python

            import httpx
            
            response = httpx.post("http://localhost:8000/freshness")
            print(response.json())

      .. tab:: curl

         .. code-block:: bash

            curl -X POST "http://localhost:8000/freshness"

      .. tab:: Go

         .. code-block:: go

            package main

            import (
                "bytes"
                "encoding/json"
                "fmt"
                "net/http"
            )

            func main() {
                resp, _ := http.Post("http://localhost:8000/freshness", 
                    "application/json", bytes.NewBuffer([]byte{}))
                defer resp.Body.Close()
                
                var result map[string]interface{}
                json.NewDecoder(resp.Body).Decode(&result)
                fmt.Println(result)
            }

      .. tab:: Scala

         .. code-block:: scala

            import java.net.http.{HttpClient, HttpRequest, HttpResponse}
            import java.net.URI

            object FreshnessExample {
                def main(args: Array[String]): Unit = {
                    val client = HttpClient.newHttpClient()
                    
                    val request = HttpRequest.newBuilder()
                        .uri(URI.create("http://localhost:8000/freshness"))
                        .header("Content-Type", "application/json")
                        .POST(HttpRequest.BodyPublishers.ofString("{}"))
                        .build()
                    
                    val response = client.send(request, 
                        HttpResponse.BodyHandlers.ofString())
                    println(response.body())
                }
            }

3. **Run a timeliness check**

   .. tabs::

      .. tab:: Python

         .. code-block:: python

            import httpx
            
            response = httpx.post("http://localhost:8000/timeliness", json={
                "lookback_minutes": 60
            })
            print(response.json())

      .. tab:: curl

         .. code-block:: bash

            curl -X POST "http://localhost:8000/timeliness" \
                 -H "Content-Type: application/json" \
                 -d '{
                   "lookback_minutes": 60
                 }'

      .. tab:: Go

         .. code-block:: go

            package main

            import (
                "bytes"
                "encoding/json"
                "fmt"
                "net/http"
            )

            type TimelinessRequest struct {
                LookbackMinutes int `json:"lookback_minutes"`
            }

            func main() {
                data := TimelinessRequest{
                    LookbackMinutes: 60,
                }
                
                jsonData, _ := json.Marshal(data)
                resp, _ := http.Post("http://localhost:8000/timeliness", 
                    "application/json", bytes.NewBuffer(jsonData))
                defer resp.Body.Close()
                
                var result map[string]interface{}
                json.NewDecoder(resp.Body).Decode(&result)
                fmt.Println(result)
            }

      .. tab:: Scala

         .. code-block:: scala

            import java.net.http.{HttpClient, HttpRequest, HttpResponse}
            import java.net.URI
            import play.api.libs.json.Json

            object TimelinessExample {
                def main(args: Array[String]): Unit = {
                    val client = HttpClient.newHttpClient()
                    
                    val json = Json.obj(
                        "lookback_minutes" -> 60
                    ).toString()
                    
                    val request = HttpRequest.newBuilder()
                        .uri(URI.create("http://localhost:8000/timeliness"))
                        .header("Content-Type", "application/json")
                        .POST(HttpRequest.BodyPublishers.ofString(json))
                        .build()
                    
                    val response = client.send(request, 
                        HttpResponse.BodyHandlers.ofString())
                    println(response.body())
                }
            }

4. **Run a Celery queue check**

   .. tabs::

      .. tab:: Python

         .. code-block:: python

            import httpx
            
            response = httpx.post("http://localhost:8000/celery/monitor-queue")
            print(response.json())

      .. tab:: curl

         .. code-block:: bash

            curl -X POST "http://localhost:8000/celery/monitor-queue"

      .. tab:: Go

         .. code-block:: go

            package main

            import (
                "bytes"
                "encoding/json"
                "fmt"
                "net/http"
            )

            func main() {
                resp, _ := http.Post("http://localhost:8000/celery/monitor-queue", 
                    "application/json", bytes.NewBuffer([]byte{}))
                defer resp.Body.Close()
                
                var result map[string]interface{}
                json.NewDecoder(resp.Body).Decode(&result)
                fmt.Println(result)
            }

      .. tab:: Scala

         .. code-block:: scala

            import java.net.http.{HttpClient, HttpRequest, HttpResponse}
            import java.net.URI

            object CeleryMonitorExample {
                def main(args: Array[String]): Unit = {
                    val client = HttpClient.newHttpClient()
                    
                    val request = HttpRequest.newBuilder()
                        .uri(URI.create("http://localhost:8000/celery/monitor-queue"))
                        .header("Content-Type", "application/json")
                        .POST(HttpRequest.BodyPublishers.ofString("{}"))
                        .build()
                    
                    val response = client.send(request, 
                        HttpResponse.BodyHandlers.ofString())
                    println(response.body())
                }
            }

Step 5: Configure Anomaly Detection
-----------------------------------

.. note::
   Set ``WATCHER_AUTO_CREATE_ANOMALY_DETECTION_RULES=true`` to automatically create anomaly detection rules for new pipelines.

1. **Create an anomaly detection rule**

   .. tabs::

      .. tab:: Python

         .. code-block:: python

            import httpx
            
            response = httpx.post("http://localhost:8000/anomaly_detection_rule", json={
                "pipeline_id": 1,
                "metric_field": "total_rows",
                "z_threshold": 3.0,
                "minimum_executions": 30,
                "lookback_days": 30
            })
            print(response.json())

      .. tab:: curl

         .. code-block:: bash

            curl -X POST "http://localhost:8000/anomaly_detection_rule" \
                 -H "Content-Type: application/json" \
                 -d '{
                   "pipeline_id": 1,
                   "metric_field": "total_rows",
                   "z_threshold": 3.0,
                   "minimum_executions": 30,
                   "lookback_days": 30
                 }'

      .. tab:: Go

         .. code-block:: go

            package main

            import (
                "bytes"
                "encoding/json"
                "fmt"
                "net/http"
            )

            type AnomalyRuleRequest struct {
                PipelineID        int     `json:"pipeline_id"`
                MetricField       string  `json:"metric_field"`
                ZThreshold        float64 `json:"z_threshold"`
                MinimumExecutions int     `json:"minimum_executions"`
                LookbackDays      int     `json:"lookback_days"`
            }

            func main() {
                data := AnomalyRuleRequest{
                    PipelineID:        1,
                    MetricField:       "total_rows",
                    ZThreshold:        3.0,
                    MinimumExecutions: 30,
                    LookbackDays:      30,
                }
                
                jsonData, _ := json.Marshal(data)
                resp, _ := http.Post("http://localhost:8000/anomaly_detection_rule", 
                    "application/json", bytes.NewBuffer(jsonData))
                defer resp.Body.Close()
                
                var result map[string]interface{}
                json.NewDecoder(resp.Body).Decode(&result)
                fmt.Println(result)
            }

      .. tab:: Scala

         .. code-block:: scala

            import java.net.http.{HttpClient, HttpRequest, HttpResponse}
            import java.net.URI
            import play.api.libs.json.Json

            object AnomalyRuleExample {
                def main(args: Array[String]): Unit = {
                    val client = HttpClient.newHttpClient()
                    
                    val json = Json.obj(
                        "pipeline_id" -> 1,
                        "metric_field" -> "total_rows",
                        "z_threshold" -> 3.0,
                        "minimum_executions" -> 30,
                        "lookback_days" -> 30
                    ).toString()
                    
                    val request = HttpRequest.newBuilder()
                        .uri(URI.create("http://localhost:8000/anomaly_detection_rule"))
                        .header("Content-Type", "application/json")
                        .POST(HttpRequest.BodyPublishers.ofString(json))
                        .build()
                    
                    val response = client.send(request, 
                        HttpResponse.BodyHandlers.ofString())
                    println(response.body())
                }
            }

2. **Anomaly detection runs automatically** after each successful pipeline execution

Step 6: Web Pages
-----------------

1. **Check system health**

   Visit: http://localhost:8000/diagnostics

2. **View API documentation**

   Visit: http://localhost:8000/scalar

3. **View reporting dashboard**

   Visit: http://localhost:8000/reporting

Next Steps
----------

- **Set up scheduled monitoring**: Configure cron jobs to ping the monitoring endpoints 
    - (see :doc:`../guides/monitoring` - "Scheduled Monitoring" section)
- **Configure Slack alerts**: Add your Slack webhook URL for notifications 
    - (see :doc:`../guides/monitoring` - "Slack Integration" section)
- **Set up anomaly detection rules**: Create rules for your specific metrics 
    - (see :doc:`../guides/anomaly_detection` - "Creating Detection Rules" section)
- **Explore the web pages**: Monitor system health & performance and access reporting dashboard 
    - (see :doc:`../api/endpoints` - "Diagnostics Web Page" and "Reporting Dashboard Web Page" sections)
