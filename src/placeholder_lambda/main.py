"""Runs as Placeholder Lambda.

Raises-
    error: lambda exception
Returns-
    [dict]:

"""
from typing import Dict
import os
import json
import boto3

from .custom_encoder import CustomEncoder


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


def build_response(status_code, body=None) -> Dict:
    response = {
        'status_code': status_code,
        'headers': {
            'Content-type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
    }
    if body is not None:
        response['body'] = json.dumps(body, cls=CustomEncoder)
    return response


def get_product(product_id) -> Dict:
    response = table.get_item(
        Key={
            'product_id': product_id
        }
    )
    if 'Item' in response:
        return build_response(200, response['Item'])
    else:
        return build_response(404, {'Message': f"Product_id {product_id} not found."})


def get_products() -> Dict:
    response = table.scan()
    result = response['Items']

    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStarKey=response['LastEvaluatedKey'])
        result.extend(response['Items'])
    body = {
        'products': result
    }
    return build_response(200, body)


def save_product(request_body) -> Dict:
    table.put_item(Item=request_body)
    body = {
        'Operation': 'SAVE',
        'Message': 'SUCCESS',
        'Item': request_body
    }
    return build_response(200, body)


def modify_product(product_id, update_key, update_value) -> Dict:
    response = table.update_item(
        Key={
            'product_id': product_id
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


def delete_product(product_id) -> Dict:
    response = table.delete_item(
        Key={
            'product_id': product_id
        },
        ReturnValues='ALL_OLD'
    )
    body = {
        'Operation': 'DELETE',
        'Message': "SUCCESS",
        'deletedItem': response
    }
    return build_response(200, body)


def lambda_handler(event: dict, _context: dict) -> Dict:
    """Main lambda handler for api gateway Lambda."""

    print(event)
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