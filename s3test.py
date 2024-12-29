import boto3
from ibyeolnote import settings
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

def upload_test_file():
    s3 = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name='ap-northeast-2'
    )

    try:
        s3.upload_file('test.txt', 'ibyeolnote-ai-static-s3', 'test.txt')
        print("Upload Successful")
    except FileNotFoundError:
        print("The file was not found")
    except NoCredentialsError:
        print("Credentials not available")
    except PartialCredentialsError:
        print("Incomplete credentials provided")

if __name__ == "__main__":
    with open('test.txt', 'w') as f:
        f.write('This is a test file for S3 upload.')
    upload_test_file()