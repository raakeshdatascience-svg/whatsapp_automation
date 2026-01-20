import openai

# Initialize the OpenAI client with DeepSeek's API key and base URL
client = openai.OpenAI(api_key="sk-847377f5ee3b4b769666698abc380e09", base_url="https://api.deepseek.com")

def chat_with_deepseek(user_input):
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_input},
        ],
        stream=False
    )
    return response.choices[0].message.content

# Terminal-based chatbot loop
print("DeepSeek Chatbot (type 'exit' to quit)\n")
while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        print("Goodbye!")
        break
    response = chat_with_deepseek(user_input)
    print(f"DeepSeek: {response}\n")
