import os
import boto3
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
table = dynamodb.Table('UserProfile')

def lambda_handler(event, context):
    try: 
        user_ID = event['requestContext']['identity']['cognitoIdentityId']
        profile = get_profile(user_ID)
        return {
                'statusCode': 200,
                'headers':{'Content-Type': 'application/json'},
                'body': profile['Item']
            } 
    except Exception as e:
        print(e)
        return {'statusCode': 400} 

def get_profile(username: str) -> dict:
    profile = table.get_item(
        Key = {
            'Username': username
        }
    )
    return profile     
        


        
#testing
def test_update_profile():
    test_event = {
        'requestContext': {
            'identity': {
                'cognitoIdentityId': '0893be13-3d6c-489e-9029-63e4b28945cb'
            }
        }
    }

    print(lambda_handler(test_event, {}))

test_update_profile()

