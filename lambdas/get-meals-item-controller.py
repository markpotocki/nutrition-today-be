import boto3
import os

PATH_PARAM = 'id'
TABLE_NAME = os.environ['DYNAMO_TABLE_NAME']
dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    username = event['requestContext']['identity']['cognitoIdentityId']
    meal_id = event['pathParameters'][PATH_PARAM]

    try:
        meal = get_meals_item(username, meal_id)
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': meal
        }
    except Exception as e:
        print(e)
        return {'statusCode': 500}

def get_meals_item(username: str, id: str) -> dict:
    table = dynamodb.Table(TABLE_NAME)
    meal = table.get_item(
        Key={
            'Username': username,
            'ID': id
        }
    )
    return meal['Item']
