"""
ETL Project - ULD Data Processing Demo

This Dagster project demonstrates ETL workflows for processing ULD (Unit Load Device) codes.
"""

from dagster import Definitions, load_assets_from_modules

from .assets import uld_assets
from .resources import db_resource

all_assets = load_assets_from_modules([uld_assets])

# Definitions is read and loaded when the Dagster server starts up.
# It loads all assets and resources. Resource instances are created
# when asset execution needs that resource.
defs = Definitions(
    assets=all_assets,
    resources={
        "database": db_resource,  # This key matches the argument name in raw_uld_records
    },
)
