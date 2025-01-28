import boto3
import os
from PIL import Image
import io
from botocore.exceptions import ClientError

class S3Helper:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        self.bucket_name = os.getenv('S3_BUCKET_NAME', 'credit-card-images')

    def get_image_url(self, file_path: str) -> str:
        """Generate a presigned URL for the image"""
        try:
            print(f"Generating URL for {file_path} in bucket {self.bucket_name}")
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': file_path
                },
                ExpiresIn=3600  # URL valid for 1 hour
            )
            return url
        except ClientError as e:
            print(f"Error generating presigned URL: {e}")
            return None

    def get_credit_card_image(self, card_name: str):
        """Retrieve credit card image from S3"""
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=f"{card_name}.png"
            )
            image_data = response['Body'].read()
            
            # Open and resize image
            image = Image.open(io.BytesIO(image_data))
            # Resize while maintaining aspect ratio
            max_size = (400, 400)
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            return image
        except Exception as e:
            print(f"Error retrieving image: {str(e)}")
            return None 