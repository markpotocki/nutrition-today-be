import boto3
from boto3.dynamodb.conditions import Key
import os

os.environ['DYNAMO_TABLE_NAME'] = 'Meals'

TABLE_NAME = os.environ['DYNAMO_TABLE_NAME']
dynamodb = boto3.resource('dynamodb')
KEY_NAME = 'Username'

def lambda_handler(event, context):
    username = event['requestContext']['identity']['cognitoIdentityId']
    try:
        meals = get_meals(username)
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': meals
        }
    except Exception as e:
        print(e)
        return {'statusCode': 500}

def get_meals(username: str) -> list[dict]:
    table = dynamodb.Table(TABLE_NAME)
    response = table.query(
        KeyConditionExpression=Key(KEY_NAME).eq(username)
    )
    return response['Items']

test_event = {
    'requestContext': {
        'identity': {
            'cognitoIdentityId': '123123'
        }
    }
}

response = lambda_handler(test_event, {})
print(response)