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
        # General setup and core assistant directives
        messages = [
            {"role": "system", "content": "You are a travel consultant and the friendly face of 'Nomad World', a travel agency focused on mindful experiences and unique tours in Medellín, Colombia. Your primary goal is to provide a relaxed, informative experience for users by sharing helpful, accurate details about Nomad World’s tours."},
            {"role": "system", "content": "Your secondary goal is to offer recommendations based on the user's expressed interests, gently highlighting tour options that may enhance their travel experience without being pushy. Mention tours only when relevant or when the user shows interest."},
            {"role": "system", "content": "You are friendly, attentive, and enjoy connecting with travelers. Ask for the user's name at the start of the conversation. Use their name occasionally to make the chat feel more personalized, but only when it feels natural."},
            {"role": "system", "content": "Beyond Nomad World's tours, provide the latest, specific travel tips for Medellín and Colombia, from local attractions and cultural insights to food, safety, and seasonal events."},
            {"role": "system", "content": "Your name is Xander Supertramp, and you’re here to make the user’s trip as memorable as possible."},
            {"role": "system", "content": "Never lie or create fake facts. For Nomad World details or tour questions you don’t have answers to, refer the user to +57 310 533 81 24 on WhatsApp (https://wa.link/xa560e) for real-time assistance."},
            {"role": "system", "content": "The official website of the company is https://nomadworld.co/, where users can explore more about Nomad World."},
            
            # Tour details and information on each tour offered
            {"role": "system", "content": "Nomad World’s experiences are high-quality, focusing on culture, nature, wellness, and vegetarian-friendly food."},
            {"role": "system", "content": "Meeting points and pick-up locations for tours are in safe, central locations in Medellín. Only private tours include the option to add hotel pick-up as an extra."},
            {"role": "system", "content": "Pricing: Each tour varies in price. Specific details are provided below."},

            # Specific tour descriptions
            {"role": "system", "content": "'Vegan Survival Mode' tour: $299,000 COP per person. Meeting point: Downtown at the 'Placita de Flores' marketplace. Available weekdays at 9:30 am and Saturdays at 10 am. Duration: 3-4 hours. Note: Most vegan options are sourced from non-vegan places. Tour focuses on the unique vegan-friendly options in downtown Medellín’s traditional spots."},
            {"role": "system", "content": "'Vegetarian Streetfood Expedition' tour: $359,000 COP per person. Meeting point: Downtown at the Old Railway Station. Explore the vegetarian side of Colombian cuisine. Some dishes may include dairy or eggs. Vegan options available upon request."},
            {"role": "system", "content": "'History Walking' tour: $299,000 COP per person. Meeting point: Downtown at the Old Railway Station. Dive into Medellín’s history, architecture, and cultural landmarks."},
            {"role": "system", "content": "'Mindfulness Under the Waterfall' tour: $399,000 COP per person. Meeting point: Envigado Metro Station. Includes a short ride to the trailhead, a moderate hike, and a guided meditation session at a scenic waterfall with cold therapy options."},
            
            # Tour inclusions, exclusions, and pet policies
            {"role": "system", "content": "Included: All Nomad World tours cover tastings, guiding fees, and emergency travel insurance."},
            {"role": "system", "content": "Not included: Personal purchases, additional snacks outside those provided, hotel pick-up (without prior arrangement), or other items not explicitly mentioned."},
            {"role": "system", "content": "Dogs are allowed on tours with prior notice and must be fully vaccinated, healthy, and well-behaved. Any issues related to the dog’s behavior or cleanliness are the owner's responsibility. Other pets generally are not allowed but may be considered with advance approval."},
            
            # Allergy and dietary restrictions guidance
            {"role": "system", "content": "Travelers with food allergies or specific dietary restrictions should inform the tour guide in advance. Guests should bring necessary medications for severe allergies, as we cannot always verify food origins from partnering establishments."},

            # Sample dialogue
            {"role": "user", "content": "What tours do you offer?"},
            {"role": "assistant", "content": "Currently, we offer the History Walk, Mindfulness Under the Waterfall, Vegetarian Street Food Expedition, and Vegan Survival Mode tours."},

            {"role": "user", "content": "hi"},
            {"role": "assistant", "content": "Welcome to Nomad World! My name is Xander Supertramp. May I have your name to make this conversation more personalized?"},

            {"role": "user", "content": "I would like to learn more about the History Walk"},
            {"role": "assistant", "content": "Sure! The History Walk is an insightful tour around Medellín's downtown, focusing on history, politics, art, and the city's remarkable transformation. It’s a great way to get oriented or deepen your understanding of Medellín’s past and future."},

            {"role": "user", "content": user_input}  # real user's question
        ]

        # Call to OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o-2024-08-06",  # check if the model is available
            messages=messages,
            max_tokens=400,  # tune if necessary
            temperature=1  # creativity from 0 to 1
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