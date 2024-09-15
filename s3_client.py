import boto3

# Initialize S3 client
s3_client = boto3.client('s3')

# Function to generate a pre-signed URL for private S3 objects
def generate_presigned_url(s3_uri):
    try:
        # Check if the URI is in the correct format
        if not s3_uri.startswith('s3://'):
            raise ValueError(f"Invalid S3 URI format: {s3_uri}. Must start with 's3://'")

        # Parse bucket name and object key from the S3 URI
        uri_parts = s3_uri.replace("s3://", "").split("/", 1)  # Split into bucket and object key
        if len(uri_parts) < 2:
            raise ValueError(f"Invalid S3 URI: {s3_uri}. Couldn't parse bucket and object key.")
        
        bucket_name = uri_parts[0]
        object_key = uri_parts[1]
        
        # Generate the pre-signed URL
        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': object_key},
            ExpiresIn=3600  # URL expires in 1 hour
        )
        return presigned_url

    except Exception as e:
        raise RuntimeError(f"Error generating pre-signed URL: {e}")
