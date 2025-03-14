import os

import streamlit as st
import boto3
import json
import time
import logging
from botocore.exceptions import BotoCoreError, ClientError
from botocore.eventstream import EventStream  # ✅ Import EventStream properly

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Read environment variables for aws profile and bedrock agent
AWS_PROFILE = os.environ.get("AWS_PROFILE")
AWS_REGION = os.environ.get("AWS_REGION", "eu-central-2")
BEDROCK_AGENT_ID = os.environ.get("BEDROCK_AGENT_ID")
BEDROCK_AGENT_ALIAS_ID = os.environ.get("BEDROCK_AGENT_ALIAS_ID")

# Initialize AWS Session
session = boto3.Session(profile_name=AWS_PROFILE)

# Initialize Bedrock Agent client
client = session.client('bedrock-agent-runtime', region_name=AWS_REGION)

# Function to communicate with Bedrock Agent
def generate_response_with_agent(prompt, session_id="user-session-123"):
    if not isinstance(prompt, str) or len(prompt) > 500:
        return "Invalid input detected. Please refine your question."

    max_retries = 3
    retry_delay = 2
    for attempt in range(max_retries):
        try:
            response = client.invoke_agent(
                agentId=BEDROCK_AGENT_ID,
                agentAliasId=BEDROCK_AGENT_ALIAS_ID,
                sessionId=session_id,
                inputText=prompt
            )

            logger.info(f"API Response Metadata: {response.get('ResponseMetadata')}")

            # Check if response contains an event stream
            event_stream = response.get("completion")
            if not event_stream or not isinstance(event_stream, EventStream):
                logger.error("Error: Expected streaming response, but did not receive completion stream.")
                return "Error: Unexpected response format from Bedrock Agent."

            # Process Streaming Response
            full_response = ""  # Store the entire response text
            for event in event_stream:
                logger.debug(f"Raw event: {event}")

                if "chunk" in event and "bytes" in event["chunk"]:
                    chunk_data = event["chunk"]["bytes"].decode("utf-8")  # Convert bytes to string
                    logger.debug(f"Decoded chunk: {chunk_data}")  # Log each chunk

                    full_response += chunk_data  # Append chunk to full response

            return full_response if full_response else "No response received from the agent."

        except (BotoCoreError, ClientError) as e:
            logger.error(f"Error invoking Bedrock Agent (Attempt {attempt+1}): {e}")
            time.sleep(retry_delay)
            retry_delay *= 2

    return "The Bedrock Agent is currently unavailable. Please try again later."

# Streamlit UI
st.set_page_config(page_title="Bedrock AI Chat", page_icon="💬", layout="centered")

# Page Styling
st.markdown("""
    <style>
    body { font-family: Arial, sans-serif; }
    .stTextInput > div > div > input { font-size: 18px !important; }
    .stButton > button { font-size: 18px !important; }
    .stChatMessage { font-size: 18px !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("💬 Talk to Assurance Data")
st.write("Ask me anything about Smart Support cases and I’ll find the best answer!")

# Chat Input & Response
user_input = st.text_input("Enter your question:")

if st.button("Ask"):
    if user_input:
        with st.spinner("Processing..."):
            response = generate_response_with_agent(user_input)
        st.write(f"🧠 AI: {response}")
    else:
        st.warning("Please enter a question first.")
