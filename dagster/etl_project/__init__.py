"""
ETL Project - ULD Data Processing Demo

This Dagster project demonstrates ETL workflows for processing ULD (Unit Load Device) codes.
"""

from dagster import Definitions, load_assets_from_modules

from .assets import uld_assets
from .resources import db_resource

all_assets = load_assets_from_modules([uld_assets])


# Define all Dagster definitions using the modern API
# When the pipeline runs, DAGster looks at your Definations
# Under resources, it should find "database" which is the resource that an asset needs back in uld_asset.py

# Definations is read and loaded when Dagster server starts up, where it loads all assets and resources
# Resource instances are created when asset execution needs that resource.
defs = Definitions(
    assets=all_assets,
    resources={
        "database": db_resource, # This key matches the argument name in raw_uld_records
    },
)
