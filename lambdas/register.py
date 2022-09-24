import base64
import boto3
import os

cognito_user_pool = os.environ['COGNITO_USER_POOL']
cognito_client = boto3.client('cognito-idp')
user_image_bucket = os.environ['S3_IMAGE_BUCKET']
s3 = boto3.resource('s3')
s3_client = boto3.client('s3')
profile_dynamo_table = os.environ['DYNAMO_TABLE_NAME']
dynamo = boto3.resource('dynamodb')


def register_lambda_handler(event, context):
    body = event['body']
    username = body['username']
    email = body['email']
    password = body['password']

    # Create account
    register_with_cognito(username, password, email)

    # Upload S3 profile image
    profile_image = body['profile_image']
    image_url = upload_user_image(username, profile_image)

    # Create profile
    first_name = body['first_name']
    last_name = body['last_name']
    height = body['height']
    weight = body['weight']
    dob = body['dob']
    create_user_profile(username, first_name, last_name, height, weight, dob)


def register_with_cognito(username: str, password: str, email: str):
    #TODO rollback on failure
    # Create User account with Cognito
    account_creation_response = cognito_client.admin_create_user(
        UserPoolId=cognito_user_pool,
        Username=username,
        UserAttributes=[{
            'Name': 'email',
            'Value': email
        }],
        MessageAction='SUPPRESS',
        DesiredDeliveryMediums=[
            'EMAIL'
        ]
    )

    set_password_response = cognito_client.admin_set_user_password(
        UserPoolId=cognito_user_pool,
        Username=username,
        Password=password,
        Permanent=True
    )


def upload_user_image(username: str, base64Image: str) -> str:
    image_type = base64Image.split(';')[0].split('/')[1]
    image_name = '{username}.{image_type}'.format(username=username, image_type=image_type)
    obj = s3.Object(user_image_bucket,image_name)
    obj.put(Body=base64.b64decode(base64Image.split(',')[1]))

    location = s3_client.get_bucket_location(Bucket=user_image_bucket)['LocationConstraint']
    object_url = 'https://{bucket_name}.s3-{location}.amazonaws.com/{key}'.format(
        bucket_name=user_image_bucket, location=location, key=image_name
    )
    return(object_url)


def create_user_profile(username: str, first_name: str, last_name: str,
                        height: int, weight: int, dob: str):
    table = dynamo.Table(profile_dynamo_table)
    table.put_item(
        Item={
            'Username': username,
            'first_name': first_name,
            'last_name': last_name,
            'height': height,
            'weight': weight,
            'dob': dob
        }
    )
