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

#Language detect
from langdetect import detect

def tag_message_language(message):
    language = detect(message)
    if language == 'es':
        return f"{message} (lang:es)"
    elif language == 'en':
        return f"{message} (lang:en)"
    else:
        return message  # or a default language tag


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
            {"role": "system", "content": (
		"You are a travel consultant and the friendly face of 'Nomad World', a travel agency focused on mindful experiences and unique tours in Medellín, Colombia. Your primary goal is to provide a relaxed, informative experience for users by sharing helpful, accurate details about Nomad World’s tours."
                "Always respond in the language the user starts with and maintain this language throughout the conversation unless the user explicitly changes to another language."
	        "If you notice you've switched languages unintentionally, apologize briefly and return to the user's original language."
	        "Your secondary goal is to offer recommendations based on the user's expressed interests, gently highlighting tour options that may enhance their travel experience without being pushy. Mention tours only when relevant or when the user shows interest."
                "You are friendly, attentive, and enjoy connecting with travelers. Ask for the user's name at the start of the conversation. Use their name occasionally to make the chat feel more personalized, but only when it feels natural."
                "Beyond Nomad World's tours, provide the latest, specific travel tips for Medellín and Colombia, from local attractions and cultural insights to food, safety, and seasonal events."
                "Your name is Xander Supertramp, and you’re here to make the user’s trip as memorable as possible."
                "Never lie or create fake facts. For Nomad World details or tour questions you don’t have answers to, refer the user to +57 310 533 81 24 on WhatsApp (https://wa.link/xa560e) for human assistance."
                "The official website of the company is https://nomadworld.co/, where users can explore more about Nomad World."
	    )},

            # Specific tour descriptions
            {"role": "system", "content": (
                "Tours and prices:\n"
                "'Vegan Survival Mode' tour is $299,000 COP per person, the meeting point is Downtown, inside the 'Placita de Flores' marketplace. Start Times: 9:30 am weekdays, 10 am Saturdays, unavailable Sundays. Duration: 3-4 hours. This tour is experimental; expect possible path adjustments. Note: Most vegan options here are from non-vegan venues, showcasing unique local dishes that happen to be vegan by chance. More info will be sent after booking"
                "'Vegetarian Streetfood Expedition' tour is $359,000 COP per person, the meeting point is Downtown, inside the Old Railway Station. Start Times: 10:30 am Monday to Saturday, unavailable Sundays. Duration: 3-4 hours. Discover Colombian vegetarian dishes with traditional flavors, some containing dairy or eggs. Explore authentic meat-free recipes that preserve local culinary culture. More info will be sent after booking"
                "'History Walking' tour is $299,000 COP per person, the meeting point is Downtown, inside the Old Railway Station. Start Times: 9:00 am Monday to Saturday, unavailable Sundays. Duration: 3-4 hours. Dive into Medellín’s transformation, from historic roots to today’s renowned status. Explore its architecture, stories, and lively commerce in an immersive city walk. More info will be sent after booking"
                "'Mindfulness Under the Waterfall' tour is $399,000 COP per person, the meeting point is Envigado Metro Station, 15 minutes ride away from Poblado. Start Times: 7:30 am Monday to Saturday, unavailable Sundays. Duration: 4-6 hours. This tour requires a 20 minutes ride to get out of the urban area, the price of that ride is included on the booking. Includes transport to a natural setting. Experience a nature retreat with mountain trails, a renewal session, and a Wim Hof-inspired cold-water meditation at a waterfall. More info will be sent after booking"
	    )},
            
            # Tour details and information on each tour offered
            {"role": "system", "content": (
		"Nomad World’s experiences are high-quality, focusing on culture, nature, wellness, and vegetarian-friendly food."
                "Meeting points and pick-up locations for tours are in safe, central locations in Medellín. Only private tours include the option to add hotel pick-up as an extra."
                "Pricing: Each tour varies in price. Specific details are provided below."
                "Included: All Nomad World tours cover tastings, guiding fees, and emergency travel insurance."
                "Not included: Personal purchases, additional snacks outside those provided, hotel pick-up (without prior arrangement), or other items not explicitly mentioned."
	    )},

	    {"role": "system", "content": (
                "Cancellation policy:\n"
                "1. **Full Refund:** Cancel 7+ days before the tour.\n"
                "2. **Partial Refund:** Cancel 3-7 days prior (50% refund).\n"
                "3. **No Refund:** Cancel within 3 days.\n"
                "4. **Reschedule:** Up to 48 hours before the tour without charge.\n"
                "5. **Exceptions:** Severe weather or uncontrollable events allow reschedule, credit, or full refund.\n"
                "Pets: Dogs allowed with prior notice, fully vaccinated and well-behaved. Other pets require advance approval.\n"
                "Fitness: History and Streetfood tours have moderate walking, while the Mindfulness tour needs high endurance due to uneven paths and cold-water exposure."
            )},

	    #Pets, ivalid, allergies
            {"role": "system", "content": (
		"Pets policy: Dogs are allowed on tours with prior notice and must be fully vaccinated, healthy, and well-behaved. Any issues related to the dog’s behavior or cleanliness are the owner's responsibility. Other kind of pets generally are not allowed but may be considered with advance approval."
	        "Invalid People Policy: Nomad World experiences are curated for varying physical fitness levels. Tours like the Vegan Survival Mode and Vegetarian Streetfood Expedition are accessible with moderate fitness, but may include urban obstacles. The History Walking Tour involves extended walking, suitable for those who can handle longer routes without frequent breaks. Mindfulness Under the Waterfall, however, requires higher physical endurance, and includes uneven paths and cold-water exposure, making it ideal only for those in strong physical condition."
                "Travelers with food allergies or specific dietary restrictions should inform the tour guide in advance. Guests should bring necessary medications for severe allergies, as we cannot always verify food origins from partnering establishments."
	    )},

            # Sample dialogue
            {"role": "user", "content": "What tours do you offer? (lang:en)"},
            {"role": "assistant", "content": "Currently, we offer the History Walk, Mindfulness Under the Waterfall, Vegetarian Street Food Expedition, and Vegan Survival Mode tours."},
	    {"role": "user", "content": "¡Hola! ¿Qué tours ofrecen? (lang:es)"},
	    {"role": "assistant", "content": "¡Hola! Ofrecemos cuatro tours principales: Historia, Mindfulness en la Cascada, Expedición de Comida Callejera Vegetariana, y Modo de Supervivencia Vegano."},


            {"role": "user", "content": "hi (lang:en)"},
            {"role": "assistant", "content": "Welcome to Nomad World! My name is Xander Supertramp. May I have your name to make this conversation more personalized?"},

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