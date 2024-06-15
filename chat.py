import os
import google.generativeai as genai
import google.generativeai as genai

API_KEY = 'AIzaSyC8kopd_HFCYwAjsBx6ta88OnAuOno2KYo'

# Configure the Google AI SDK with your API key
genai.configure(api_key=API_KEY)
# Configure the Google AI SDK with your API key

# Create the model configuration
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

# Initialize the GenerativeModel
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)

# Start a chat session
chat_session = model.start_chat(history=[])

# Example interaction (replace INSERT_INPUT_HERE with your input)
response = chat_session.send_message("Explain how AI works")

print(response.text)
