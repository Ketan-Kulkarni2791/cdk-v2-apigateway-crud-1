"""Runs as Placeholder Lambda.

Raises-
    error: lambda exception
Returns-
    [dict]:
"""
import os
import json
import logging
import boto3

from custom_encoder.custom_encoder import CustomEncoder

logging.getLogger().setLevel(logging.INFO)

db_table = os.environ['dynamoDBTableName']
dynamodb_client = boto3.resource('dynamodb')
table = dynamodb_client.Table(db_table)

GET_METHOD = "GET"
POST_METHOD = "POST"
PATCH_METHOD = "PATCH"
DELETE_METHOD = "DELETE"
HEALTH_PATH = "/health"
PRODUCT = "/product"
PRODUCTS = "/products"


def lambda_handler(event: dict, _context: dict) -> dict:
    """Main lambda handler for api gateway Lambda."""

    logging.info("This is the event we received: %s", event)
    http_method = event["httpMethod"]
    path = event["path"]

    if http_method == GET_METHOD and path == HEALTH_PATH:
        response = build_response(200)
    elif http_method == GET_METHOD and path == PRODUCT:
        response = get_product(event['queryStringParameters']['product_id'])
    elif http_method == GET_METHOD and path == PRODUCTS:
        response = get_products()
    elif http_method == POST_METHOD and path == PRODUCT:
        response = save_product(json.loads(event['body']))
    elif http_method == PATCH_METHOD and path == PRODUCT:
        request_body = json.loads(event['body'])
        response = modify_product(
            request_body['product_id'],
            request_body['update_key'],
            request_body['update_value']
        )
    elif http_method == DELETE_METHOD and path == PRODUCT:
        request_body = json.loads(event['body'])
        response = delete_product(request_body['product_id'])
    else:
        response = build_response(404, 'Not Found')

    return response


def build_response(status_code, body=None) -> dict:
    response = {
        'statusCode': status_code,
        'headers': {
            'Content-type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
    }
    if body is not None:
        response['body'] = json.dumps(body, cls=CustomEncoder)
    return response


def get_product(product_id) -> dict:
    """
    URL : https://w3nj9p4xh6.execute-api.ap-south-1.amazonaws.com/prod/product?product_id=1003 
    Params : {"product_id": 1003}
    Response : {
        "price": 480.0,
        "productid": "1003",
        "color": "Blue"
    }
    """
    response = table.get_item(
        Key={
            'productid': product_id
        }
    )
    if 'Item' in response:
        return build_response(200, response['Item'])
    else:
        return build_response(404, {'Message': f"Product_id {product_id} not found."})


def get_products() -> dict:
    response = table.scan()
    result = response['Items']

    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStarKey=response['LastEvaluatedKey'])
        result.extend(response['Items'])
    body = {
        'products': result
    }
    return build_response(200, body)


def save_product(request_body) -> dict:
    """
    URL : https://w3nj9p4xh6.execute-api.ap-south-1.amazonaws.com/prod/product 
    Body: {
        "productid": "1001",
        "color": "Red",
        "price": 100
    }
    Response : {
        "Operation": "SAVE",
        "Message": "SUCCESS",
        "Item": {
            "productid": "1001",
            "color": "Red",
            "price": 100
        }
    }
    """
    table.put_item(Item=request_body)
    body = {
        'Operation': 'SAVE',
        'Message': 'SUCCESS',
        'Item': request_body
    }
    return build_response(200, body)


def modify_product(product_id, update_key, update_value) -> dict:
    """
    URL : https://w3nj9p4xh6.execute-api.ap-south-1.amazonaws.com/prod/product 
    Body: {
        "product_id": "1002",
        "update_key": "price",
        "update_value": 10000
    }
    Response : {
        "Operation": "UPDATE",
        "Message": "SUCCESS",
        "UpdatedAttributes": {
            "Attributes": {
                "price": 10000.0
            },
            "ResponseMetadata": {
                "RequestId": "NT29J83955T4TJ2UQ97V3BIPCRVV4KQNSO5AEMVJF66Q9ASUAAJG",
                "HTTPStatusCode": 200,
                "HTTPHeaders": {
                    "server": "Server",
                    "date": "Mon, 13 Mar 2023 09:01:40 GMT",
                    "content-type": "application/x-amz-json-1.0",
                    "content-length": "38",
                    "connection": "keep-alive",
                    "x-amzn-requestid": "NT29J83955T4TJ2UQ97V3BIPCRVV4KQNSO5AEMVJF66Q9ASUAAJG",
                    "x-amz-crc32": "822034527"
                },
                "RetryAttempts": 0
            }
        }
    }
    """
    response = table.update_item(
        Key={
            'productid': product_id
        },
        UpdateExpression=f"Set {update_key} = :value",
        ExpressionAttributeValues={
            ':value': update_value
        },
        ReturnValues='UPDATED_NEW'
    )
    body = {
        'Operation': 'UPDATE',
        'Message': 'SUCCESS',
        'UpdatedAttributes': response
    }
    return build_response(200, body)


def delete_product(product_id) -> dict:
    """

    URL : https://w3nj9p4xh6.execute-api.ap-south-1.amazonaws.com/prod/product 
    Body: {
        "product_id": "1001"
    }
    Response : {
        "Operation": "DELETE",
        "Message": "SUCCESS",
        "deletedItem": {
            "Attributes": {
                "price": 100.0,
                "productid": "1001",
                "color": "Red"
            },
            "ResponseMetadata": {
                "RequestId": "0UHIE5PG3H2VKRIPSIK97AU74JVV4KQNSO5AEMVJF66Q9ASUAAJG",
                "HTTPStatusCode": 200,
                "HTTPHeaders": {
                    "server": "Server",
                    "date": "Mon, 13 Mar 2023 12:45:05 GMT",
                    "content-type": "application/x-amz-json-1.0",
                    "content-length": "81",
                    "connection": "keep-alive",
                    "x-amzn-requestid": "0UHIE5PG3H2VKRIPSIK97AU74JVV4KQNSO5AEMVJF66Q9ASUAAJG",
                    "x-amz-crc32": "1764259650"
                },
                "RetryAttempts": 0
            }
        }
    }
    
    """
    response = table.delete_item(
        Key={
            'productid': product_id
        },
        ReturnValues='ALL_OLD'
    )
    body = {
        'Operation': 'DELETE',
        'Message': "SUCCESS",
        'deletedItem': response
    }
    return build_response(200, body)