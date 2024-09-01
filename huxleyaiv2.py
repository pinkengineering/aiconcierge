import os
import streamlit as st
import boto3
import json
from pinecone import Pinecone, Index

# Initialize the Bedrock client
client = boto3.client('bedrock-runtime', region_name='us-east-1')

# Initialize the Pinecone client
api_key = '742a9082-b0b0-49bf-b923-512653de7fce'
pc = Pinecone(api_key=api_key)

# Connect to your Pinecone index
index_name = "ai-index-v2"
index = Index(name=index_name, api_key=api_key, host='https://ai-index-v2-tc2pbf1.svc.aped-4627-b74a.pinecone.io')

def get_encoded_query(query):
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

def query_knowledge_base(query, knowledge_base_id):
    encoded_query = get_encoded_query(query)

    response = index.query(
        vector=encoded_query,
        top_k=5,
        include_metadata=True
    )

    context = ""
    for match in response['matches']:
        raw_metadata = match.get('metadata', {})
        if isinstance(raw_metadata, str):
            parsed_metadata = json.loads(raw_metadata)
        else:
            parsed_metadata = raw_metadata

        source = parsed_metadata.get('source', 'Unknown Source')
        text = parsed_metadata.get('text', 'No Text Available')
        context += f"{source}: {text} "
    
    return context

def generate_response(prompt, context):
    try:
        full_prompt = f"\n\nHuman: {prompt}\n\n{context}\n\nAssistant:"

        payload = {
            "modelId": "anthropic.claude-v2",
            "contentType": "application/json",
            "accept": "*/*",
            "body": json.dumps({
                "prompt": full_prompt,
                "max_tokens_to_sample": 300,
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
        st.error(f"Error invoking Bedrock model: {e}")
        return None

# Streamlit interface
st.title("Huxley AI Concierge")

# Placeholder for chatbot history
if 'history' not in st.session_state:
    st.session_state['history'] = []

# User input
user_input = st.text_input("Hi, how can I help you today?:", "")

if user_input:
    # Step 1: Query the knowledge base to get context
    context = query_knowledge_base(user_input, "VQQQX9CXWT")  # Replace with your actual knowledge base ID

    # Step 2: Generate a response using the retrieved context
    response = generate_response(user_input, context)

    if response:
        # Update history
        st.session_state['history'].append((user_input, response))
    else:
        st.error("Failed to generate a response.")

# Display the conversation history
for i, (user_text, bot_response) in enumerate(st.session_state['history']):
    st.write(f"**You:** {user_text}")
    st.write(f"**Huxley AI Concierge:** {bot_response}")
    st.write("---")
