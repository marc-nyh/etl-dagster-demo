"""
ETL Project - ULD Data Processing Demo

This Dagster project demonstrates ETL workflows for processing ULD (Unit Load Device) codes.
"""

from dagster import Definitions, load_assets_from_modules

from .assets import uld_assets
from .resources import PostgresResource

all_assets = load_assets_from_modules([uld_assets])

# Define the resource configuration
# In a real app, use EnvVar("POSTGRES_PASSWORD") instead of hardcoding!
db_resource = PostgresResource(
    host="postgres",  # Docker service name
    user="etl_user",
    password="etl_password",
    database="etl_db"
)

# Define all Dagster definitions using the modern API
defs = Definitions(
    assets=all_assets,
    resources={
        "database": db_resource, # This key matches the argument name in raw_uld_records
    },
)
