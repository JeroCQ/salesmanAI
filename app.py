from flask import Flask, request, jsonify, render_template
import os
import time
import logging

#This Imports de apikey from .env and checks is working
from dotenv import load_dotenv
load_dotenv('/mnt/c/AIchatbot/.env')
openai_api_key = os.getenv("OPENAI_API_KEY")
print(openai_api_key)
print(os.getcwd())

# this registers all the messages
logging.basicConfig(filename='chatbot_interactions.log', level=logging.INFO, format='%(asctime)s - %(message)s')


# simulation for testing
USE_SIMULATION = False

app = Flask(__name__)

# without simulation
client = None
if not USE_SIMULATION:
    try:
        from openai import OpenAI
        client = OpenAI(api_key=openai_api_key)
    except ImportError:
        raise ImportError("OpenAI library is not installed. Please install it to use the real API.")

# calls limit per minute
API_CALL_LIMIT = 5
CALL_WINDOW = 60  # en segundos

# these are for controlling the calls
api_call_count = 0
last_call_time = time.time()

# get reponse funtion (simulated or real)
def get_response(user_input):
    global api_call_count, last_call_time

    # controls number of calls to the API
    current_time = time.time()
    if current_time - last_call_time > CALL_WINDOW:
        # restart the number after the time period
        api_call_count = 0
        last_call_time = current_time

    if api_call_count >= API_CALL_LIMIT:
        return "Límite de llamadas a la API alcanzado. Intenta más tarde."

    # Increase call count
    api_call_count += 1

    if USE_SIMULATION:
        return simulated_openai_response(user_input)
    else:
        return openai_response(user_input)

# simulated responses
def simulated_openai_response(user_input):
    responses = {
        "hola": "¡Hola! ¿En qué puedo ayudarte?",
        "cuéntame sobre tu agencia": "Somos una agencia de viajes que ofrece experiencias únicas y personalizadas.",
        "¿qué tours tienes?": "Ofrecemos tours por la ciudad, recorridos culturales y naturales, y mucho más.",
        # Agrega más respuestas simuladas aquí si es necesario
    }
    return responses.get(user_input.lower(), "Lo siento, no entiendo tu pregunta.")

# real answers
def openai_response(user_input):
    try:
        messages = [
            # Instructions for the asistant (system role)
#            {"role": "system", "content": ""},
            {"role": "system", "content": "You are the salesman of the company 'Nomad World'. Your main goal is to subtly sell the tours that the company offers without being pushy"},
            {"role": "system", "content": "Your second goal is to bring all the information the user requests"},
            {"role": "system", "content": "Your third goal is give useful, updated and specific travel recommendations for Medellin and Colombia"},
            {"role": "system", "content": "Your name is Xander Supertramp"},
            {"role": "system", "content": "You are the friendliest guy ever"},
            {"role": "system", "content": "Ask for the user's name once, if you get it, talk to them recalling it, so they know that you remember it"},
            {"role": "system", "content": "'Nomad World' is located in Medellín, Colombia"},
            {"role": "system", "content": "'Nomad World' focuses in unique and mindful experciences"},
            {"role": "system", "content": "The official website of the company is https://nomadworld.co/"},
            {"role": "system", "content": "If you don't know the info the client requires or the if the client wants to talk to a real person, share them my whatsapp (+57 310 533 81 24) and a direct link to it https://wa.link/xa560e"},

            # FAQ examples
#            {"role": "user", "content": ""},
#            {"role": "assistant", "content": ""},

#  MISSING:
#	pick up
#	meeting points
#	prices
#	whats included
#	whats not included

            {"role": "user", "content": "What tours do you offer?"},
            {"role": "assistant", "content": "At the moment I can offer to you History Walk, Mindfulness Under the Waterfall, Vegetarian Street Food Expedition and Vegan Survival Mode"},

            # Dialogue examples
#            {"role": "user", "content": ""},
#            {"role": "assistant", "content": ""},


            {"role": "user", "content": "hi"},
            {"role": "assistant", "content": "¡Welcome to Nomad World! My name is Xander Supertramp, I'm here to assist you. Can I know your name, please?"},

            {"role": "user", "content": "I would like to learn more about the History Walk"},
            {"role": "assistant", "content": "Sure, It's a walk around downtown area talking about the history, politics, art, architecture or economics of the region depending on your preferences, this is perfect whether for getting some context of the place your landing or to get a deeper understandig of this place that you may have loved already"},

            {"role": "user", "content": "That Mindfulness Under the Waterfall tour sounds interesting"},
            {"role": "assistant", "content": "Oh! It is! Let me introduce what it is about: Deep in the jungle, getting the top of the mountains there's a beautiful but super cold waterfall, there we use the famous technique called WIm Hof Method to do a cold therapy. This includes a short but challenging hike through mud and river crossings"},

            {"role": "user", "content": "How is it possible to have vegetarian streetfood in a non vegetarian friendly city?"},
            {"role": "assistant", "content": "Not that easy, being honest. But here we are, with a great route of around 10 different stopd of pure and super traditional food and drinks, its reputation precedes it"},

            {"role": "user", "content": "Good, I'm vegan, what's that vegan tour about?"},
            {"role": "assistant", "content": "Glad to know, Congratulations! It would be a pleasure to have you in the tour we designed for you. Wasn't easy but we finally hacked the local gastronomy for you. jus local gatronomy walking around downtown, enjoying the views and the culture. It's amazing"},

            # Instruction to keep the conversation with the actual user
            {"role": "user", "content": user_input}  # real user's question
        ]
        response = client.chat.completions.create(
            model="gpt-4o-2024-08-06",  # check if the model is available
            messages=messages,
            max_tokens=400,  # tune if necessary
	    temperature=1  #creativity from 0 to 1
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {str(e)}"

# Route to manage the user's requests
@app.route('/chat', methods=['POST'])

def chat():
    user_message = request.json.get("message")

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    chat_response = get_response(user_message)

    # register the interaction
    logging.info(f"User: {user_message} | Bot: {chat_response}")

    return jsonify({"response": chat_response}), 200

# Route for the Home Page
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)