import boto3
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
table = dynamodb.Table('UserProfile')

def lambda_handler(event, context):
    try: 
        new_profile = event['body']
        new_profile['Username'] = event['requestContext']['identity']['cognitoIdentityId']

        return {
                'statusCode': 204
            } 
    except Exception as e:
        print(e)
        return {'statusCode': 400} 

def post_profile(new_profile: dict) -> None:
    table.put_item(
        Item = new_profile
    )   
