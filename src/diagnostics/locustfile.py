import random
import time

import pendulum
from locust import HttpUser, between, task


class PipelineExecutionUser(HttpUser):
    """
    Simulates 1000 pipelines executing hourly on the same cadence.
    Each user represents one pipeline that runs every hour.
    """

    _user_count = 0
    weight = 998  # 998 out of 1000 users

    wait_time = between(300, 300)  # Wait 1 hour between executions (3600 seconds)

    def on_start(self):
        PipelineExecutionUser._user_count += 1
        self.pipeline_number = PipelineExecutionUser._user_count
        self.pipeline_name = f"hourly_pipeline_{self.pipeline_number:03d}"
        print(f"Pipeline {self.pipeline_name} starting hourly execution cycle")

    def create_pipeline(self):
        """Create pipeline using get_or_create_pipeline endpoint"""
        with self.client.post(
            "/pipeline",
            json={
                "name": self.pipeline_name,
                "pipeline_type_name": "hourly_load_test_type",
                "freshness_number": 6,
                "freshness_datepart": "hour",
                "timeliness_number": 15,
                "timeliness_datepart": "minute",
            },
            catch_response=True,
        ) as response:
            if response.status_code in [200, 201]:
                return response.json()["id"]
            else:
                response.failure(
                    f"Failed to create pipeline {self.pipeline_name}: {response.status_code} - {response.text}"
                )

    @task(1)
    def execute_pipeline_hourly(self):
        """
        Simulates a complete pipeline execution cycle:
        1. Create/get pipeline
        2. Start execution
        3. Wait for processing time (simulate work)
        4. End execution with results
        """
        # Step 1: Create pipeline using get_or_create_pipeline endpoint
        pipeline_id = self.create_pipeline()

        # Step 2: Start pipeline execution
        with self.client.post(
            "/start_pipeline_execution",
            json={
                "pipeline_id": pipeline_id,
                "full_load": False,
                "start_date": pendulum.now("UTC").isoformat(),
            },
            catch_response=True,
        ) as start_response:
            if start_response.status_code not in [200, 201]:
                error_msg = f"Failed to start pipeline {pipeline_id}: {start_response.status_code}"
                error_msg += f"\nRequest: {start_response.request.body}"
                error_msg += f"\nResponse: {start_response.text}"
                error_msg += f"\nHeaders: {dict(start_response.headers)}"
                start_response.failure(error_msg)
                return

            execution_id = start_response.json()["id"]

        # Step 3: Simulate processing time (30 seconds to 10 minutes)
        processing_time = random.randint(30, 600)
        time.sleep(processing_time)

        # Step 4: End pipeline execution with realistic data (occasionally anomalous)
        # 5% chance of generating anomalous data to trigger anomaly detection
        is_anomalous = random.random() < 0.01

        if is_anomalous:
            # Generate anomalous data that should trigger alerts
            data = {
                "total_rows": random.randint(
                    500000, 2000000
                ),  # Much higher than normal
                "inserts": random.randint(50000, 200000),  # Much higher than normal
                "updates": random.randint(25000, 100000),  # Much higher than normal
                "soft_deletes": random.randint(5000, 20000),  # Much higher than normal
                "duration_seconds": random.randint(
                    1800, 7200
                ),  # Much longer than normal (30min-2hr)
            }
        else:
            # Normal data
            data = {
                "total_rows": random.randint(1000, 100000),
                "inserts": random.randint(100, 10000),
                "updates": random.randint(50, 5000),
                "soft_deletes": random.randint(0, 100),
                "duration_seconds": processing_time,
            }

        with self.client.post(
            "/end_pipeline_execution",
            json={
                "id": execution_id,
                "pipeline_id": pipeline_id,
                "completed_successfully": random.choices(
                    [True, False], weights=[95, 5]
                )[0],  # 95% success rate
                "end_date": pendulum.now("UTC").isoformat(),
                **data,
            },
            catch_response=True,
        ) as end_response:
            if end_response.status_code != 204:
                end_response.failure(
                    f"Failed to end pipeline execution {execution_id}: {end_response.status_code} - {end_response.text}"
                )

        print(
            f"Pipeline {pipeline_id} completed execution {execution_id} in {processing_time}s"
        )


class MonitoringUser(HttpUser):
    """
    Dedicated user for system monitoring (timeliness, freshness, celery checks)
    Runs every 5 minutes without being blocked by pipeline execution sleep
    """

    weight = 1  # 1 out of 1000 users
    wait_time = between(300, 300)  # Every 5 minutes

    def on_start(self):
        print("Monitoring user started - will run system checks every 5 minutes")

    @task(1)
    def run_system_checks(self):
        """Run system-wide checks every 5 minutes"""
        # Freshness check
        with self.client.post(
            "/freshness", catch_response=True, timeout=10
        ) as response:
            if response.status_code != 200:
                response.failure(
                    f"Freshness check failed: {response.status_code} - {response.text}"
                )

        # Timeliness check
        with self.client.post(
            "/timeliness",
            json={"lookback_minutes": 60},
            catch_response=True,
            timeout=10,
        ) as response:
            if response.status_code != 200:
                response.failure(
                    f"Timeliness check failed: {response.status_code} - {response.text}"
                )

        # Celery queue monitoring
        with self.client.post(
            "/celery/monitor-queue", catch_response=True, timeout=10
        ) as response:
            if response.status_code != 200:
                response.failure(
                    f"Celery queue monitoring failed: {response.status_code} - {response.text}"
                )


class HeartbeatUser(HttpUser):
    """
    Dedicated user for heartbeat checks
    Runs every minute to check if the API is responding
    """

    weight = 1  # 1 out of 1000 users
    wait_time = between(60, 60)

    def on_start(self):
        print("Heartbeat user started - will check API health every minute")

    @task(1)
    def run_heartbeat_check(self):
        """Run heartbeat check every minute"""
        with self.client.get("/", catch_response=True, timeout=5) as response:
            if response.status_code != 200:
                response.failure(
                    f"Heartbeat check failed: {response.status_code} - {response.text}"
                )
