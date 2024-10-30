import boto3
import json

# Initialize the Bedrock client
client = boto3.client('bedrock-runtime', region_name='us-east-1')

# Function to encode the query using Bedrock model
def get_encoded_query(query):
    if not query.strip():  # Guard against empty input
        raise ValueError("The query cannot be empty")

    model_id = "amazon.titan-embed-text-v2:0"
    payload = {
        "modelId": model_id,
        "contentType": "application/json",
        "accept": "*/*",
        "body": json.dumps({
            "inputText": query,
            "dimensions": 512,
            "normalize": True
        })
    }

    response = client.invoke_model(
        modelId=payload['modelId'],
        body=payload['body'],
        contentType=payload['contentType'],
        accept=payload['accept']
    )

    response_body = response['body'].read().decode('utf-8')
    embedding = json.loads(response_body)['embedding']
    return embedding

# Function to generate a response using Bedrock model
def generate_response(prompt, context):
    try:
        full_prompt = f'Human: {prompt}\n\nContext: {context}\n\nAssistant:'
        payload = {
            "modelId": "anthropic.claude-3-haiku-20240307-v1:0",
            "contentType": "application/json",
            "accept": "*/*",
            "body": json.dumps({
                "prompt": full_prompt,
                "max_tokens_to_sample": 200,
                "temperature": 0.5,
                "top_k": 250,
                "top_p": 1,
                "stop_sequences": ["\n\nHuman:"],
                "anthropic_version": "bedrock-2023-05-31"
            })
        }

        response = client.invoke_model(
            modelId=payload['modelId'],
            body=payload['body'],
            contentType=payload['contentType'],
            accept=payload['accept']
        )

        response_body = response['body'].read().decode('utf-8')
        generated_text = json.loads(response_body)['completion']
        return generated_text

    except Exception as e:
        raise RuntimeError(f"Error invoking Bedrock model: {e}")
