#!/usr/bin/env python3
"""
Test script to verify S3 configuration and connectivity
"""
import os
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

def test_s3_connection():
    """Test S3 connection and permissions"""
    try:
        # Initialize S3 client
        s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )

        bucket_name = os.getenv('S3_BUCKET_NAME')
        bucket_path = os.getenv('S3_BUCKET_PATH')
        aws_region = os.getenv('AWS_REGION', 'us-east-1')

        print(f"Testing S3 connection to bucket: {bucket_name}")

        # Test bucket access
        s3_client.head_bucket(Bucket=bucket_name)
        print("✓ S3 bucket access successful")

        # Test list objects (to verify read permissions)
        objects = s3_client.list_objects_v2(Bucket=bucket_name, MaxKeys=1)
        print("✓ S3 read permissions verified")

        # Test upload permissions (optional - creates a test file)
        test_key = os.path.join(bucket_path, "test-connection.txt")
        test_content = b"S3 connection test"

        s3_client.put_object(
            Bucket=bucket_name,
            Key=test_key,
            Body=test_content,
            ContentType='text/plain'
        )
        print("✓ S3 write permissions verified")

        print(f"Test file uploaded to: {test_key}")
        url = f"https://{bucket_name}.s3.{aws_region}.amazonaws.com/{test_key}"
        print(f"Test file URL: {url}")

        # Check if URL is reachable
        try:
            response = requests.get(url)
            if response.status_code == 200:
                print("✓ URL is reachable")
            else:
                print(f"✗ URL is not reachable: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"✗ URL is not reachable: {e}")

        # Clean up test file
        s3_client.delete_object(Bucket=bucket_name, Key=test_key)
        print("✓ S3 delete permissions verified")

        return True

    except NoCredentialsError:
        print("✗ S3 credentials not found or invalid")
        return False
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'NoSuchBucket':
            print(f"✗ Bucket '{bucket_name}' does not exist")
        elif error_code == 'AccessDenied':
            print(f"✗ Access denied to bucket '{bucket_name}'")
        else:
            print(f"✗ S3 error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

def check_environment():
    """Check if all required environment variables are set"""
    required_vars = [
        'AWS_ACCESS_KEY_ID',
        'AWS_SECRET_ACCESS_KEY',
        'S3_BUCKET_NAME',
        'S3_BUCKET_PATH',
        'AWS_REGION'
    ]

    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        print("✗ Missing environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        return False
    else:
        print("✓ All required environment variables are set")
        return True

if __name__ == "__main__":
    print("=== S3 Configuration Test ===")

    # Check environment variables
    env_ok = check_environment()
    if not env_ok:
        print("\nPlease set the missing environment variables and try again.")
        exit(1)

    print()

    # Test S3 connection
    s3_ok = test_s3_connection()

    print()
    if s3_ok:
        print("🎉 S3 configuration is working correctly!")
    else:
        print("❌ S3 configuration test failed.")
        print("\nPlease check:")
        print("1. AWS credentials are correct")
        print("2. S3 bucket exists and is accessible")
        print("3. IAM permissions include s3:PutObject, s3:GetObject, s3:DeleteObject")
