import boto3
import os
from datetime import datetime

TABLE_NAME = os.environ['DYNAMO_TABLE_NAME']
dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    username = event['requestContext']['identity']['cognitoIdentityId']
    goal = event['body']

    try:
        create_goal(username, goal)
        return {
            'statusCode': 204
        }
    except Exception as e:
        print(e)
        return {'statusCode': 500}


def create_goal(username: str, goal: dict) -> None:
    table = dynamodb.Table(TABLE_NAME)
    goal['Username'] = username
    now = datetime.now()
    goal['Time'] = str(now)

    table.put_item(
        Item=goal
    )