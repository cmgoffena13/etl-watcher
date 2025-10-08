import time

import httpx
import pendulum
from pipeline import PIPELINE_CONFIG
from utils import ETLMetrics, sync_pipeline, track_pipeline_execution

parent_pipeline_execution_id = 5  # Dynamically passed from fake ticker script
tickers = ["AAPL", "META"]  # Dynamically passed from fake ticker script

next_watermark = pendulum.now().date().to_date_string()

pipeline_response = sync_pipeline(PIPELINE_CONFIG, next_watermark)

params = {
    "apiKey": "XXXXX",
}


if pipeline_response.active is False:
    print("Pipeline is not active, skipping execution")
    exit()


@track_pipeline_execution(
    pipeline_id=pipeline_response.id,
    parent_pipeline_execution_id=parent_pipeline_execution_id,
)
def extract_data(
    tickers: list[str], watermark: pendulum.date, current_date: pendulum.date
):
    all_records = []
    total_rows = 0
    for ticker in tickers:
        date = watermark  # Make sure we reset the watermark for each ticker
        while date < current_date:
            response = httpx.get(
                f"https://api.polygon.io/v1/open-close/{ticker}/{watermark}",
                params=params,
            )

            record = response.json()

            if response.status_code == 429:
                wait_time = 30
                print(f"Rate limit exceeded. Waiting {wait_time} seconds...")
                time.sleep(wait_time)
                continue

            if record["status"] == "OK":
                all_records.append(record)
            date = date.add(days=1)

        print(all_records)  # Save records somewhere for each ticker
        total_rows += len(all_records)
    return ETLMetrics(
        completed_successfully=True,
        total_rows=total_rows,
    )
