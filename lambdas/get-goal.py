import boto3
import os

PATH_PARAM = 'id'
TABLE_NAME = os.environ['DYNAMO_TABLE_NAME']
dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    username = event['requestContext']['identity']['cognitoIdentityId']
    goal_id = event['pathParameters'][PATH_PARAM]

    try:
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
            'Username': username,
            'Time': goal_id
        }
    )
    return goal
