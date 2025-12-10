"""
Dag Hello World Dagster Package

Hello World Dagster module for testing
"""

from dagster import Definitions

from .assets import (
    sample_asset,
)
from .resources import dag_hello_world_io_manager

# Define all Dagster components
defs = Definitions(
    assets=[
        sample_asset,
    ],
    resources={
        "io_manager": dag_hello_world_io_manager,
    },
)
