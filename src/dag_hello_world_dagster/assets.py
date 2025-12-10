"""
Dagster assets for Dag Hello World.

Hello World Dagster module for testing
"""

import os
from typing import Dict, Any
from dagster import asset, AssetExecutionContext


@asset(
    key_prefix=["dag_hello_world"],
    description="Sample asset demonstrating basic patterns",
    compute_kind="python",
)
def sample_asset(context: AssetExecutionContext) -> Dict[str, Any]:
    """
    Sample asset that demonstrates the basic structure.

    Replace this with your actual asset logic.

    Returns:
        Dict containing asset output data
    """
    context.log.info("Sample asset executing...")

    # Your asset logic here
    result = {
        "status": "success",
        "message": "Sample asset completed",
        "timestamp": context.run_id,
    }

    context.log.info(f"Asset completed: {result}")
    return result
