"""Runs as Placeholder Lambda.

Raises-
    error: lambda exception
Returns-
    [dict]:

"""
import os
import io
import json


def lambda_handler(event: dict, _context: dict) -> dict:
    """Main lambda handler for Incoming Data to S3 Transform Location Lambda."""

    return {
        "Status": "Hello from lambda"
    }