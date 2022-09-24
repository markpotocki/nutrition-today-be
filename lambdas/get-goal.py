import boto3
from boto3.dynamodb.conditions import Key
import os

PATH_PARAM = 'id'
TABLE_NAME = os.environ['DYNAMO_TABLE_NAME']
KEY_NAME = 'Username'
dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    username = event['requestContext']['identity']['cognitoIdentityId']
    goal_id = event['pathParameters'][PATH_PARAM]

    try:
        if goal_id == 'latest':
            goal = get_latest_goal(username)
        else:
            goal = get_goal(username, goal_id)
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': goal
        }
    except Exception as e:
        print(e)
        return {'statusCode': 500}


def get_goal(username: str, goal_id: str) -> dict:
    table = dynamodb.Table(TABLE_NAME)
    goal = table.get_item(
        Key={
            KEY_NAME: username,
            'Time': goal_id
        }
    )
    return goal

def get_latest_goal(username: str) -> dict:
    table = dynamodb.Table(TABLE_NAME)
    goal = table.query(
        KeyConditionExpression=Key(KEY_NAME).eq(username),
        Limit=1
    )
    return goal
