from openai_tools import GPTClient

API_KEY = "chatgpt_key"
client = GPTClient(api_key=API_KEY)
response = client.get_response("Write a warm welcome message for a new member joining a WhatsApp group.")
print(response)