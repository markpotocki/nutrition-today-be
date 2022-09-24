import boto3
from boto3.dynamodb.conditions import Key
import os

TABLE_NAME = os.environ['DYNAMO_TABLE_NAME']
KEY_NAME = 'Username'
dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    username = event['requestContext']['identity']['cognitoIdentityId']
    try:
        goals = get_goals(username)
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': goals
        }
    except Exception as e:
        print(e)
        return {'statusCode': 500}


def get_goals(username: str) -> dict:
    table = dynamodb.Table(TABLE_NAME)
    response = table.query(
        KeyConditionExpression=Key(KEY_NAME).eq(username)
    )
    return response['Items']
