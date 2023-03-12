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

getMethod = "GET"
postMethod = "POST"
patchMethod = "PATCH"
deleteMethod = "DELETE"
healthPath = "/health"
product = "/product"
products = "/products"


def buildResponse(statusCode, body=None) -> Dict:
    response = {
        'statusCode': statusCode,
        'headers': {
            'Content-type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
    }
    if body is not None:
        response['body'] = json.dumps(body, cls=CustomEncoder)
    return response

def getProduct(productId) -> Dict:
    response = table.get_item(
        Key={
            'productId': productId
        }
    )
    if 'Item' in response:
        return buildResponse(200, response['Item'])
    else:
        return buildResponse(404, {'Message': f"ProductId {productId} not found."})

def getProducts() -> Dict:
    response = table.scan()
    result = response['Items']

    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStarKey=response['LastEvaluatedKey'])
        result.extend(response['Items'])
    body = {
        'products': result
    }
    return buildResponse(200, body)

def saveProduct(requestBody) -> Dict:
    table.put_item(Item=requestBody)
    body = {
        'Operation': 'SAVE',
        'Message': 'SUCCESS',
        'Item': requestBody
    }
    return buildResponse(200, body)

def modifyProduct(productId, updateKey, updateValue) -> Dict:
    response = table.update_item(
        Key={
            'productId': productId
        },
        UpdateExpression=f"Set {updateKey} = :value",
        ExpressionAttributeValues={
            ':value': updateValue
        },
        ReturnValues='UPDATED_NEW'
    )
    body = {
        'Operation': 'UPDATE',
        'Message': 'SUCCESS',
        'UpdatedAttributes': response
    }
    return buildResponse(200, body)

def deleteProduct(productId) -> Dict:
    response = table.delete_item(
        Key={
            'productId': productId
        },
        ReturnValues='ALL_OLD'
    )
    body = {
        'Operation': 'DELETE',
        'Message': "SUCCESS",
        'deletedItem': response
    }
    return buildResponse(200, body)

def lambda_handler(event: dict, _context: dict) -> str:
    """Main lambda handler for api gateway Lambda."""

    httpMethod = event["httpMethod"]
    path = event["path"]

    if httpMethod == getMethod and path == healthPath:
        response = buildResponse(200)
    elif httpMethod == getMethod and path == product:
        response = getProduct(event['queryStringParameters']['productId'])
    elif httpMethod == getMethod and path == products:
        response = getProducts()
    elif httpMethod == postMethod and path == product:
        response = saveProduct(json.loads(event['body']))
    elif httpMethod == patchMethod and path == product:
        requestBody = json.loads(event['body'])
        response = modifyProduct(requestBody['productId'], requestBody['updateKey'],
                                 requestBody['updateValue']
                                )
    elif httpMethod == deleteMethod and path == product:
        requestBody = json.loads(event['body'])
        response = deleteProduct(requestBody['productId'])
    else:
        response = buildResponse(404, 'Not Found')
    
    return response