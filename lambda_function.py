import json
import os
import uuid
import boto3
from botocore.exceptions import ClientError

# Initialize AWS SDK clients outside handler for connection reuse across cold starts
dynamodb = boto3.resource('dynamodb')
ses_client = boto3.client('ses', region_name=os.environ.get('AWS_REGION', 'us-east-1'))

# Retrieve environment variables or set production defaults
TABLE_NAME = os.environ.get('TABLE_NAME', 'ordersTable')
ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@example.com')

table = dynamodb.Table(TABLE_NAME)

def send_admin_email(customer_name, phone, address, package):
    """
    Constructs and sends an order notification email via AWS Simple Email Service (SES).
    """
    subject = f"🚨 NEW ORDER: {customer_name}"
    body_text = f"""
NEW ORDER RECEIVED!

Customer Name: {customer_name}
Phone Number: {phone}
Delivery Address: {address}
Package Selected: {package}
    """

    try:
        ses_client.send_email(
            Source=ADMIN_EMAIL,
            Destination={'ToAddresses': [ADMIN_EMAIL]},
            Message={
                'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                'Body': {'Text': {'Data': body_text, 'Charset': 'UTF-8'}}
            }
        )
        print(f"SES Notification sent successfully to {ADMIN_EMAIL}")
    except ClientError as e:
        print(f"Failed to send SES email: {e.response['Error']['Message']}")
        raise e

def lambda_handler(event, context):
    """
    Main entry point for AWS Lambda triggered by API Gateway HTTP POST requests.
    """
    try:
        # Parse payload body from API Gateway proxy integration
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})

        # Extract order parameters
        customer_name = body.get('customer_name', 'N/A')
        phone = body.get('phone_number', 'N/A')
        address = body.get('delivery_address', 'N/A')
        package = body.get('package_selected', 'N/A')

        # Generate unique order ID
        order_id = str(uuid.uuid4())[:8]

        # 1. Store order record in DynamoDB
        table.put_item(
            Item={
                'order_id': order_id,
                'customer_name': customer_name,
                'phone_number': phone,
                'delivery_address': address,
                'package_selected': package,
                'status': 'PENDING'
            }
        )
        print(f"Order {order_id} successfully saved to DynamoDB table '{TABLE_NAME}'.")

        # 2. Trigger SES email alert
        send_admin_email(customer_name, phone, address, package)

        # 3. Return clean HTTP 200 response to caller
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'message': 'Order processed successfully',
                'order_id': order_id
            })
        }

    except Exception as e:
        print(f"Execution Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({'error': 'Failed to process order submission.'})
        }
