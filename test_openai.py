from openai_tools import GPTClient

API_KEY = "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"
client = GPTClient(api_key=API_KEY)
response = client.get_response("Write a warm welcome message for a new member joining a WhatsApp group.")
print(response)