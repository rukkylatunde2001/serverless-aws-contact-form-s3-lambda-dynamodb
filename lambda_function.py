import json
import boto3
import uuid
from datetime import datetime

# Connect to DynamoDB
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('ContactFormSubmissions')

def lambda_handler(event, context):
    try:
        # Parse the incoming form data
        body = json.loads(event['body'])
        name = body['name']
        email = body['email']
        message = body['message']

        # Save to DynamoDB
        table.put_item(Item={
            'submissionId': str(uuid.uuid4()),
            'name': name,
            'email': email,
            'message': message,
            'timestamp': datetime.now().isoformat()
        })

        # Return success response
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({'message': 'Form submitted successfully!'})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({'error': str(e)})
        }
