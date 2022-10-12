import boto3
import os
import uuid
import json
from urllib.parse import unquote_plus
from PIL import Image
from datetime import datetime
from twilio.rest import Client 

s3_client = boto3.client('s3')
dynamoTable = boto3.resource(
    'dynamodb', region_name=str(os.environ['REGION_NAME'])
).Table(str(os.environ['DYNAMODB_TABLE']))

def s3_thumbnail_generator(event, context):
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = unquote_plus(record['s3']['object']['key'])
        download_path = '/tmp/{}{}'.format(uuid.uuid4(), key)
        upload_path = '/tmp/resized-{}'.format(key)
        s3_client.download_file(bucket, key, download_path)
        
        make_thumbnail(download_path, upload_path) # make a thumbnail
        resized_image_name = new_filename(key) # create a new file name for resized bucket
        s3_client.upload_file(upload_path, '{}-resized'.format(bucket), resized_image_name) # upload a resized image to the resized bucket
        
        saveToDynamoDB(key, bucket) # save data to dynamo db
        sendEmail(bucket, 'info@asukamethod.com', 'info@asukamethod.com') # send a notification email
        sendSMS(bucket) # send a notification sms

def make_thumbnail(image_path, resized_path):
    with Image.open(image_path) as image:
        image.thumbnail(tuple(x / 2 for x in image.size))
        image.save(resized_path)

def new_filename(key):
    key_split = key.rsplit('.', 1)
    return str(uuid.uuid4()) + '_' + key_split[0] + "_thumbnail.png"

def sendEmail(bucket, sender_email, receiver_email):
    import smtplib, ssl

    port = 587  # For starttls
    smtp_server = 'smtp.gmail.com'
    password = '...password...'
    subject = 'image upload'
    body = 'image is uploaded on ' + bucket
    message = 'Subject: {}\n\n{}'.format(subject, body)
    context = ssl.create_default_context()

    with smtplib.SMTP(smtp_server, port) as server:
        try:
            server.ehlo() # identify ourselves to smtp gmail client
            server.starttls(context=context) # secure our email with tls encryption
            server.ehlo() # re-identify ourselves as an encrypted connection
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message)
            server.quit()
        except:
            print('Something went wrong...')  
  
def sendSMS(bucket):
    account_sid = '......' 
    auth_token = '....' 
    client = Client(account_sid, auth_token) 
    
    message = client.messages.create(  
                messaging_service_sid='.....', 
                body='image is uploaded on ' + bucket,      
                to='...phone number...' 
            ) 
    
def saveToDynamoDB(key, bucket):
    data = dynamoTable.put_item(
        Item={
            'id': str(uuid.uuid4()),
            'bucket-name': str(bucket),
            'key': str(key),
            'createdAt': str(datetime.now()),
            'updatedAt': str(datetime.now())
        } 
    )
    response = {
        'statusCode': 200,
        'body': 'successfully created item!'
    }        
    return response

def get_all_data(event, context):
    response = dynamoTable.scan()
    data = response['Items']

    while 'LastEvaluatedKey' in response:
        response = dynamoTable.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        data.extend(response['Items'])

    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': True,
        },
        'body': json.dumps(data)
    }

def get_item(event, context):
    response = dynamoTable.get_item(Key={
        'id': event['pathParameters']['id']
    })

    item = response['Item']

    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': True,
        },
        'body': json.dumps(item)
    }

def delete_item(event, context):
    response = dynamoTable.delete_item(Key={
        'id': event['pathParameters']['id']
    })
    message = 'deleted succesfully!'
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': True,
        },
        'body': message
    }