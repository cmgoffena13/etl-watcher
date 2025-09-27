import random
import time

import pendulum
from locust import HttpUser, between, task


class PipelineExecutionUser(HttpUser):
    """
    Simulates 1000 pipelines executing hourly on the same cadence.
    Each user represents one pipeline that runs every hour.
    """

    wait_time = between(300, 300)  # Wait 1 hour between executions (3600 seconds)

    def on_start(self):
        # Each user gets assigned a pipeline number (1-1000)
        self.pipeline_number = random.randint(1, 1000)
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
                # Log as failure in Locust
                response.failure(
                    f"Failed to create pipeline {self.pipeline_name}: {response.status_code} - {response.text}"
                )
                return 1  # Fallback ID

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
                # Log as failure in Locust with detailed error info
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

        # Step 4: End pipeline execution with realistic data
        with self.client.post(
            "/end_pipeline_execution",
            json={
                "id": execution_id,
                "pipeline_id": pipeline_id,
                "completed_successfully": random.choices(
                    [True, False], weights=[95, 5]
                )[0],  # 95% success rate
                "end_date": pendulum.now("UTC").isoformat(),
                "total_rows": random.randint(1000, 100000),
                "inserts": random.randint(100, 10000),
                "updates": random.randint(50, 5000),
                "soft_deletes": random.randint(0, 100),
                "duration_seconds": processing_time,
            },
            catch_response=True,
        ) as end_response:
            if end_response.status_code != 204:
                # Log as failure in Locust
                end_response.failure(
                    f"Failed to end pipeline execution {execution_id}: {end_response.status_code} - {end_response.text}"
                )

        print(
            f"Pipeline {pipeline_id} completed execution {execution_id} in {processing_time}s"
        )

    @task(1)
    def run_system_checks(self):
        """
        Run system-wide checks every 15 minutes (only a few users)
        """
        current_time = pendulum.now("UTC")
        # Only run system checks every 15 minutes and only for one user
        if current_time.minute % 15 == 0 and self.pipeline_number == 1:
            # Freshness check
            with self.client.post("/freshness", catch_response=True) as response:
                if response.status_code != 200:
                    response.failure(
                        f"Freshness check failed: {response.status_code} - {response.text}"
                    )

            # Timeliness check
            with self.client.post(
                "/timeliness", json={"lookback_minutes": 60}, catch_response=True
            ) as response:
                if response.status_code != 200:
                    response.failure(
                        f"Timeliness check failed: {response.status_code} - {response.text}"
                    )

            # Celery queue monitoring
            with self.client.post(
                "/celery/monitor-queue", catch_response=True
            ) as response:
                if response.status_code != 200:
                    response.failure(
                        f"Celery queue monitoring failed: {response.status_code} - {response.text}"
                    )

    @task(1)
    def run_heartbeat_check(self):
        """
        Run heartbeat check every 5 minutes (only a few users)
        """
        current_time = pendulum.now("UTC")
        # Only run heartbeat check every 5 minutes and only for 5% of users
        if current_time.minute % 5 == 0 and random.random() < 0.05:
            with self.client.get("/", catch_response=True, timeout=5) as response:
                if response.status_code != 200:
                    response.failure(
                        f"Heartbeat check failed: {response.status_code} - {response.text}"
                    )
