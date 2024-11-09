import json
import boto3
import os

# Initialize AWS clients with region configuration
s3_client = boto3.client('s3', region_name='eu-west-1')
rekognition_client = boto3.client('rekognition', region_name='eu-west-1')

# Retrieve the bucket name from an environment variable
BUCKET_NAME = os.environ.get("BUCKET_NAME")

def lambda_handler(event, context):
    if not BUCKET_NAME:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Bucket name is not set in environment variables"})
        }

    # List all objects in the S3 bucket
    paginator = s3_client.get_paginator('list_objects_v2')
    rekognition_results = []  # Store the results

    for page in paginator.paginate(Bucket=BUCKET_NAME):
        for obj in page.get('Contents', []):
            # Perform PPE detection using Rekognition
            rekognition_response = rekognition_client.detect_protective_equipment(
                Image={
                    'S3Object': {
                        'Bucket': BUCKET_NAME,
                        'Name': obj['Key']
                    }
                },
                SummarizationAttributes={
                    'MinConfidence': 80,  # Confidence level threshold
                    'RequiredEquipmentTypes': ['FACE_COVER']
                }
            )
            rekognition_results.append(rekognition_response)

    return {
        "statusCode": 200,
        "body": json.dumps(rekognition_results),
    }

# Example standalone execution
if __name__ == "__main__":
    print(lambda_handler(None, None))
