from flask import Flask, render_template, request, jsonify, session
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from chat import ChatBot
import os
import logging
import json
from datetime import datetime
import uuid
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def resolve_credentials_path(credentials_path):
    """Resolve relative paths to absolute paths"""
    if not credentials_path:
        return None
    
    # If it's already an absolute path and exists, return it
    if os.path.isabs(credentials_path) and os.path.exists(credentials_path):
        return credentials_path
    
    # Convert relative path to absolute path
    base_dir = Path(__file__).parent.absolute()
    absolute_path = os.path.join(base_dir, credentials_path)
    
    # Check if the file exists
    if os.path.exists(absolute_path):
        return absolute_path
    
    # Try other common locations
    possible_locations = [
        absolute_path,
        os.path.join(os.getcwd(), credentials_path),
        os.path.join(os.getcwd(), 'credentials', os.path.basename(credentials_path)),
        os.path.join(Path(__file__).parent.absolute(), credentials_path),
    ]
    
    for location in possible_locations:
        if location and os.path.exists(location):
            return location
    
    return credentials_path

# Session management
@app.before_request
def make_session_permanent():
    session.permanent = True
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())

# Initialize rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Initialize ChatBot
def initialize_chatbot():
    try:
        # Verify all required environment variables are set
        required_vars = ['GOOGLE_APPLICATION_CREDENTIALS', 'GCP_PROJECT_ID', 'AGENT_ID']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        # Check if credentials file exists
        credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        resolved_path = resolve_credentials_path(credentials_path)
        
        if not resolved_path or not os.path.exists(resolved_path):
            raise ValueError(f"Credentials file not found: {resolved_path}")
        
        # Update the environment variable to the found path
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = resolved_path
        
        logging.info("Environment variables loaded successfully")
        
        chatbot = ChatBot()
        logging.info("Vertex AI ChatBot initialized successfully")
        return chatbot
        
    except Exception as e:
        logging.error(f"Error initializing ChatBot: {str(e)}")
        return None

chatbot = initialize_chatbot()

@app.route('/')
def home():
    return render_template('base.html')

@app.route('/predict', methods=['POST'])
@limiter.limit("10 per minute")
def predict():
    try:
        if not chatbot:
            logging.error("Chatbot not initialized")
            return jsonify({
                'error': 'Chatbot not initialized',
                'answer': 'Service temporarily unavailable. Please check server logs.'
            }), 503
            
        data = request.get_json()
        if not data:
            logging.error("No data received in request")
            return jsonify({
                'error': 'No data received',
                'answer': 'Please provide a valid query.'
            }), 400
        
        message = data.get('message', '').strip()
        
        if not message:
            logging.error("Empty message received")
            return jsonify({
                'error': 'Empty message',
                'answer': 'Please provide a question or message.'
            }), 400
        
        # Log the request
        logging.info(f"Processing query: {message}")
        
        # Get response from chatbot
        response = chatbot.chat(message)
        logging.info(f"Chatbot response: {response}")
        
        return jsonify(response)
        
    except Exception as e:
        error_msg = str(e)
        logging.error(f"Error in predict endpoint: {error_msg}")
        logging.exception("Full traceback:")
        return jsonify({
            'error': error_msg,
            'answer': 'An error occurred while processing your request. Please try again.'
        }), 500
    
@app.route('/health')
def health_check():
    """Health check endpoint to verify Vertex AI connectivity"""
    if chatbot:
        return jsonify({
            'status': 'healthy',
            'vertex_ai_initialized': True,
            'project_id': os.getenv('GCP_PROJECT_ID'),
            'agent_id': os.getenv('AGENT_ID')
        })
    else:
        return jsonify({
            'status': 'unhealthy',
            'vertex_ai_initialized': False,
            'error': 'Vertex AI not initialized'
        }), 500

if __name__ == '__main__':
    try:
        logging.info("Starting MQA Chatbot Server with Vertex AI...")
        app.run(debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true', 
                use_reloader=False, 
                host=os.getenv('FLASK_HOST', '127.0.0.1'),
                port=int(os.getenv('FLASK_PORT', 5000)))
    except Exception as e:
        logging.error(f"Failed to start server: {e}")