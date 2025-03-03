import os
import uuid
import base64
import boto3
import sys
from typing import Optional
from django.http import HttpRequest
from botocore.exceptions import NoCredentialsError,ClientError
from loan_management.helpers.helper import decode_base64_image

class PDFStorageService():
    
    def __init__(self, error_messages=[]) -> None:
        
        self.region_name = os.environ.get('AWS_REGION')

        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
            region_name=self.region_name
        )
        
        self.expiration = 3600
        self.bucket_name = os.environ.get('AWS_BUCKET_NAME')
        self.error_messages = error_messages
    
           
    def save_base64_pdf(self, pdf_base64: str, file_name: str = None, upload_dir: str = "media/assets/pdfs") -> Optional[str]:
        try:
            # Check if the base64 string includes the format part
            if ';base64,' in pdf_base64:
                _, base64_data = pdf_base64.split(';base64,')
            else:
                base64_data = pdf_base64

            decoded_data = base64.b64decode(base64_data)

            os.makedirs(upload_dir, exist_ok=True)

            if file_name is None or file_name == '':
                file_name = str(uuid.uuid4()) + ".pdf"

            file_path = os.path.join(upload_dir, file_name)

            with open(file_path, "wb") as file:
                file.write(decoded_data)

            return file_path
        except Exception as e:
            print(f"Error saving PDF: {e}")
            return None


    def save_base64_pdf_to_s3_signed_url(self, pdf_base64: str, file_name: str = None, upload_dir: str = None) -> Optional[str]:
        try:
            if ';base64,' in pdf_base64:
                _, base64_data = pdf_base64.split(';base64,')
            else:
                base64_data = pdf_base64

            pdf_data = base64.b64decode(base64_data)

            if file_name is None or file_name == '':
                file_name = str(uuid.uuid4()) + ".pdf"
            
            object_name = f'media/assets/{upload_dir}/{file_name}'
            
            # Upload the PDF
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=object_name,
                Body=pdf_data,
                ContentType='application/pdf'  # MIME type for PDF files
            )
            print(f"PDF uploaded to S3 bucket {self.bucket_name} with key {object_name}")
            
            return object_name
    
        except Exception as e:
            print(f"Error saving PDF: {e}")
            exc_type, _, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            error = f'exc_type: {exc_type}, fname: {fname}, line number: {exc_tb.tb_lineno}, error: {str(e)}'
            self.error_messages.append(error)
            return None

    def save_base64_image_to_s3_signed_url(self, image_base64: str, file_name: str, upload_dir: str = "media/assets/henpec") -> Optional[str]:
        try:
            image_data, file_extension, content_type = decode_base64_image(image_base64)

            if file_name is None or file_name == '':
                file_name = str(uuid.uuid4()) + file_extension
                
            object_name = f'{upload_dir}/{file_name}'
            
            try:
                self.s3_client.head_object(Bucket=self.bucket_name, Key=object_name)
            except ClientError as e:
                if e.response['Error']['Code'] == '404':
                    pass  # The object does not exist
                else:
                    raise e

            # Upload the image
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=object_name,
                Body=image_data,
                ContentType=content_type
            )
            
            return object_name

        except Exception as e:
            print(f"Error saving image: {e}")
            exc_type, _, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            error = f'exc_type: {exc_type}, fname: {fname}, line number: {exc_tb.tb_lineno}, error: {str(e)}'
            self.error_messages.append(error)
            return None

    def delete_s3_object(self,bucket_name: str, object_key: str) -> bool:
        """
        Delete an object from an S3 bucket.

        :param bucket_name: The name of the S3 bucket.
        :param object_key: The key of the object to delete.
        :return: True if the deletion was successful, False otherwise.
        """
        s3_client = boto3.client('s3')
        
        try:
            s3_client.delete_object(Bucket=self.bucket_name, Key=object_key)
            print(f"Successfully deleted {object_key} from {bucket_name}.")
            return True
        except ClientError as e:
            print(f"An error occurred: {e}")
            return False





    def generate_pdf_s3_signed_url(self, object_name: str) -> str:
        public_url = f"https://{self.bucket_name}.s3.{self.region_name}.amazonaws.com/{object_name}"
        return public_url
    
    def generate_presigned_url(self, object_name: str, expiration: int = None) -> Optional[str]:
        try:
            if expiration is None:
                expiration = self.expiration

            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': object_name
                },
                ExpiresIn=expiration
            )
            return url
        except NoCredentialsError:
            print("Credentials not available")
            return None
        except Exception as e:
            print(f"Error generating presigned URL: {e}")
            return None

    def generate_pdf_url(self, file_path: str, request: HttpRequest) -> str:
        base_url = request.build_absolute_uri('/')
        return base_url.rstrip("/") + "/" + file_path.replace("\\", "/")
