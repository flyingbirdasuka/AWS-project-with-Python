This repository demonstrates how to deploy a Python AWS Lambda function using the Serverless Framework.
The lambda function provides a full workflow for processing uploaded images. When an image is uploaded to an S3 bucket, a Lambda function:

Downloads the image and generates a thumbnail at half the original size.

Saves the thumbnail in a separate S3 bucket with a unique UUID-based filename.

Stores metadata (UUID, bucket name, key, timestamps) in DynamoDB for persistent tracking.

Sends notifications via email (SMTP) and SMS (Twilio) to inform users about the upload.

Offers API endpoints to retrieve all image metadata, fetch a specific item, and delete items from DynamoDB.

This setup creates a fully serverless image management system, combining S3, Lambda, DynamoDB, and external notifications, ideal for automating image workflows.
