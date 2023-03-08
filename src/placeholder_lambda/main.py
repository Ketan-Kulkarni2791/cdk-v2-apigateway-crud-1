"""Runs as Placeholder Lambda.

Raises-
    error: lambda exception
Returns-
    [dict]:

"""


def lambda_handler(event: dict, _context: dict) -> dict:
    """Main lambda handler for Incoming Data to S3 Transform Location Lambda."""

    print(event)
    return {
        "Status": "Hello from lambda"
    }