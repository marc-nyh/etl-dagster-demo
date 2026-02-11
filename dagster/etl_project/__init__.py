"""
ETL Project - ULD Data Processing Demo

This Dagster project demonstrates ETL workflows for processing ULD (Unit Load Device) codes.
"""

from dagster import Definitions, load_assets_from_modules

from .assets import uld_assets

all_assets = load_assets_from_modules([uld_assets])

# Define all Dagster definitions using the modern API
defs = Definitions(
    assets=all_assets,
    resources={},
)
