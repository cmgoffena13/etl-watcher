import time

import httpx
import pendulum
from pipeline import POLYGON_OPEN_CLOSE_PIPELINE_CONFIG

# Utilizing etl-watcher-sdk
from watcher import ETLMetrics, Watcher, WatcherExecutionContext

# Initiate Watcher client
watcher = Watcher("http://localhost:8000")

parent_execution_id = 5  # Dynamically passed from fake ticker script
tickers = ["AAPL", "META"]  # Dynamically passed from fake ticker script

synced_config = watcher.sync_pipeline_config(POLYGON_OPEN_CLOSE_PIPELINE_CONFIG)
params = {
    "apiKey": "XXXXX",
}


@watcher.track_pipeline_execution(
    pipeline_id=synced_config.id,
    active=synced_config.active,
    parent_execution_id=parent_execution_id,
    watermark=synced_config.watermark,
    next_watermark=synced_config.next_watermark,
)
def extract_data(watcher_context: WatcherExecutionContext, tickers: list[str]):
    watermark = pendulum.parse(watcher_context.watermark).date()
    next_watermark = pendulum.parse(watcher_context.next_watermark).date()
    print(f"Watermark: {watermark}, Next Watermark: {next_watermark}")

    all_records = []
    total_rows = 0
    for ticker in tickers:
        date = watermark  # Make sure we reset the watermark for each ticker
        while date < next_watermark:
            response = httpx.get(
                f"https://api.polygon.io/v1/open-close/{ticker}/{date}",
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
        total_rows=total_rows,
    )


print("Extracting data...")
extract_data(tickers=tickers)
