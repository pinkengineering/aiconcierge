import streamlit as st
from bedrock_client import get_encoded_query, generate_response
from pinecone_client import query_knowledge_base, init_pinecone
from s3_client import generate_presigned_url
from utils import load_environment, load_css
from PIL import Image

# Load environment variables and CSS
load_environment()
load_css('style.css')

# Initialize Pinecone index (with the host provided)
index = init_pinecone()  # Now returns the Pinecone index object

# Define the layout with two columns: one for the image and the other for the content
col1, col2 = st.columns([1, 2])  # Adjust the ratio to control the space distribution

# Left column: Add the image
with col1:
    image = Image.open("Huxley_AI.png")  
    st.image(image, caption="Huxley AI Concierge", width=200)  # Resize the image with width=200

# Right column: Add the title and input field
with col2:
    # Main Streamlit App
    st.title("Huxley AI Concierge")

    user_input_temp = st.text_input("Hi, how can I help you today?")

    if st.button("Submit"):
        with st.spinner("Huxley AI is thinking..."):
            try:
                # Step 1: Encode query using Bedrock
                encoded_query = get_encoded_query(user_input_temp)  # Get the query encoded using Bedrock
                
                # Step 2: Query Pinecone knowledge base and retrieve context
                context, source_url = query_knowledge_base(
                    index=index,  # Pass the Pinecone Index object
                    query_vector=encoded_query  # Use the encoded query vector
                )

                # Step 3: Generate response from Bedrock model
                response = generate_response(user_input_temp, context)

                # Step 4: Display response in Streamlit
                st.write(f"Huxley AI Concierge: {response}")

                if source_url:
                    # Step 5: Display the pre-signed URL as clickable text with the label "Source"
                    st.markdown(f"[Source]({source_url})")
                else:
                    st.write("No source document found.")

            except Exception as e:
                st.error(f"An error occurred: {e}")
