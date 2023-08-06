from dagster import (
    Definitions,
    load_assets_from_modules,
    define_asset_job,
    ScheduleDefinition
)

from . import assets
import os
from dotenv import  load_dotenv, dotenv_values
from github import Github

load_dotenv()

all_assets = load_assets_from_modules([assets])

defs = Definitions(
    assets=all_assets,
    schedules=[
        ScheduleDefinition(
            job=define_asset_job(name="daily_refresh", selection="*"),
            cron_schedule="@daily",
        )
    ],
    resources={"github_api": Github(os.getenv("GITHUB_ACCESS_TOKEN"))},
)






