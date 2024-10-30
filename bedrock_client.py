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
def generate_response(prompt, context, image_data=None):
    try:
        messages = [
            {
                "role": "user",
                "content": []
            }
        ]

        if image_data:
            messages[0]["content"].append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/jpeg",
                    "data": image_data
                }
            })

        messages[0]["content"].append({
            "type": "text",
            "text": f"{prompt}\n\nContext: {context}"
        })

        payload = {
            "modelId": "anthropic.claude-3-haiku-20240307-v1:0",
            "contentType": "application/json",
            "accept": "application/json",
            "body": json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1000,
                "messages": messages
            })
        }

        response = client.invoke_model(**payload)

        response_body = json.loads(response['body'].read())
        generated_text = response_body['content'][0]['text']
        return generated_text

    except Exception as e:
        raise RuntimeError(f"Error invoking Bedrock model: {e}")
