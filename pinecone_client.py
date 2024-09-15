import os
import json
import streamlit as st
from pinecone import Index
import boto3

# Initialize S3 client
s3_client = boto3.client('s3')

# Initialize Pinecone client (no longer necessary to call Pinecone client directly, we just use the host)
def init_pinecone():
    api_key = st.secrets["API_KEY"]  # Fetch API key from secrets.toml
    host = "https://ai-index-v2-tc2pbf1.svc.aped-4627-b74a.pinecone.io"  # Use the provided host

    # Create and return the Pinecone Index instance using the host
    index = Index(name="ai-index-v2", api_key=api_key, host=host)

    return index

# Function to generate a pre-signed URL for private S3 objects
def generate_presigned_url(s3_uri):
    try:
        # Ensure that the URI is correctly formatted
        if not s3_uri.startswith('s3://'):
            raise ValueError(f"Invalid S3 URI: {s3_uri}")
        
        # Parse the bucket name and object key
        uri_parts = s3_uri.replace("s3://", "").split("/", 1)
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

# Function to query Pinecone index and generate pre-signed URLs
def query_knowledge_base(index, query_vector, top_k=5):
    # Query the index
    response = index.query(
        vector=query_vector,
        top_k=top_k,
        include_metadata=True
    )

    context = ""
    presigned_url = None  # Initialize presigned_url outside the loop

    for match in response['matches']:
        raw_metadata = match.get('metadata', {})
        
        # Parse metadata if needed
        if isinstance(raw_metadata, str):
            parsed_metadata = json.loads(raw_metadata)
        else:
            parsed_metadata = raw_metadata

        # Extract text and source URI from metadata
        text = parsed_metadata.get('text', 'No Text Available')
        source_uri = parsed_metadata.get('x-amz-bedrock-kb-source-uri', None)

        context += f"- {text}\n"
        
        # If there's an S3 source URI, generate a pre-signed URL
        if source_uri:
            try:
                presigned_url = generate_presigned_url(source_uri)
            except Exception as e:
                st.error(f"Error generating pre-signed URL: {e}")
                presigned_url = None  # Set to None in case of an error

    return context, presigned_url
