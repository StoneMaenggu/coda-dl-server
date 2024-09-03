import aioboto3 # type: ignore
from botocore.exceptions import NoCredentialsError, ClientError
from fastapi import HTTPException
import os
from app.models.utils.access import access_key as key

key = key()

BUCKET_NAME = key.bucket_name
REGION_NAME = key.region
s3_access_key = key.s3_access_key
s3_secret_key = key.s3_secret_key

async def upload_to_s3(file_path: str, filename: str) -> str:
    session = aioboto3.Session()
    try:
        async with session.client(
            's3',
            aws_access_key_id=s3_access_key,
            aws_secret_access_key=s3_secret_key
        ) as s3_client:
            
            # 파일을 읽어서 S3로 업로드
            with open(file_path, 'rb') as file:
                await s3_client.put_object(
                    Body=file,
                    Bucket=BUCKET_NAME,
                    Key=filename,
                    ContentType='image/jpeg'
                )
    
        # 업로드된 파일의 URL 생성
        s3_url = f"https://{BUCKET_NAME}.s3.{REGION_NAME}.amazonaws.com/{filename}"
    
        return s3_url

    except NoCredentialsError:
        raise HTTPException(status_code=500, detail="AWS S3 Credentials are not available.")
    except ClientError as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload to S3: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
