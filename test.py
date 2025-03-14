import os

import boto3


AWS_PROFILE = os.environ.get("AWS_PROFILE")
AWS_REGION = os.environ.get("AWS_REGION", "eu-central-2")

session = boto3.Session(profile_name=AWS_PROFILE)

client = session.client('bedrock-agent-runtime', region_name=AWS_REGION)

response = client.invoke_agent(
    agentId=os.environ.get("BEDROCK_AGENT_ID"),
    agentAliasId=os.environ.get("BEDROCK_AGENT_ALIAS_ID"),
    sessionId="test-session",
    inputText="Hello, can you respond?"
)

print("\n🔹Raw API Response Metadata:", response)

# Process the EventStream response
event_stream = response.get("completion")

if not event_stream:
    print("\n No event stream received from Bedrock Agent.")
else:
    print("\n Reading EventStream...")
    full_response = ""  # Store the entire response text

    for event in event_stream:
        print(f"\n🔹 Raw Event: {event}")  # Print each event

        if "chunk" in event and "bytes" in event["chunk"]:
            chunk_data = event["chunk"]["bytes"].decode("utf-8")  # Convert bytes to string
            print(f"\n Decoded Chunk Data: {chunk_data}")  # Print raw text chunk

            full_response += chunk_data  # Append chunk to full response

    print("\n✅ Final Response from Bedrock Agent:")
    print(full_response)  # Print the full response
