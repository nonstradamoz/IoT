from flask import Flask, request, jsonify, render_template
from twilio.rest import Client
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing

# Twilio credentials
ACCOUNT_SID = 'ACc429df6aea105e33dfb3e01ace0945a9'
AUTH_TOKEN = '189dac04e15e10c9287a8ef7d7d9af40'
FROM_PHONE_NUMBER = '+13344234287'

client = Client(ACCOUNT_SID, AUTH_TOKEN)

# Predefined threshold for temperature alert
TEMPERATURE_THRESHOLD = 38.5  # Adjust as necessary

# ThingSpeak credentials
THINGSPEAK_API_KEY = '5JCQJ8673T4OVGD0'
THINGSPEAK_CHANNEL_ID = '2593821'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send-temperature', methods=['POST'])
def send_temperature():
    data = request.get_json()
    recipient = data['+919074812182']
    temperature = get_temperature()
    
    if temperature is not None:
        # Example: Check if temperature exceeds threshold
        if temperature > TEMPERATURE_THRESHOLD:
            # Send alert message
            send_alert_message(recipient, temperature)
            return jsonify({'alert': True, 'temperature': temperature})
        else:
            return jsonify({'alert': False, 'temperature': temperature})
    else:
        return jsonify({'error': 'Failed to fetch temperature'})

def get_temperature():
    try:
        url = f'https://api.thingspeak.com/channels/{THINGSPEAK_CHANNEL_ID}/feeds.json?api_key={THINGSPEAK_API_KEY}&results=1'
        response = requests.get(url)
        data = response.json()
        
        if 'feeds' in data and data['feeds']:
            temperature = float(data['feeds'][0]['field1'])  # Adjust field index based on your channel setup
            return temperature
        else:
            return None
    except Exception as e:
        print(f"Error fetching temperature: {str(e)}")
        return None

def send_alert_message(recipient, temperature):
    try:
        message_body = f"Alert: Dog's temperature is {temperature}°C. Please check."
        
        message = client.messages.create(
            body=message_body,
            from_=FROM_PHONE_NUMBER,
            to=recipient
        )
        
        print(f"Message sent to {recipient}: {message.sid}")
        return True
    except Exception as e:
        print(f"Error sending message: {str(e)}")
        return False

if __name__ == '__main__':
    app.run(debug=True)
