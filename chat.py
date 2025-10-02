from google.cloud import dialogflowcx_v3beta1 as dialogflow
from google.api_core.exceptions import GoogleAPICallError
from google.oauth2 import service_account
from google.auth.transport.requests import Request
import os
import re
import time
import logging
from urllib.parse import urlparse, quote, urlunparse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChatBot:
    def __init__(self):
        self._initialize_vertex_ai()
    
    def _get_credentials(self):
        """Get and validate credentials"""
        credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        
        if not credentials_path:
            raise ValueError("GOOGLE_APPLICATION_CREDENTIALS environment variable not set")
        
        if not os.path.exists(credentials_path):
            raise ValueError(f"Credentials file not found: {credentials_path}")
        
        try:
            credentials = service_account.Credentials.from_service_account_file(
                credentials_path,
                scopes=['https://www.googleapis.com/auth/cloud-platform']
            )
            
            # Refresh the token to ensure it's valid
            credentials.refresh(Request())
            
            return credentials
            
        except Exception as e:
            raise Exception(f"Failed to load credentials: {str(e)}")
    
    def _get_dialogflow_client_options(self, location):
        """Get client options based on region"""
        region_endpoints = {
            "us-central1": "us-central1-dialogflow.googleapis.com:443",
            "us-east1": "us-east1-dialogflow.googleapis.com:443",
            "us-west1": "us-west1-dialogflow.googleapis.com:443",
            "europe-west1": "europe-west1-dialogflow.googleapis.com:443",
            "europe-west2": "europe-west2-dialogflow.googleapis.com:443",
            "europe-west3": "europe-west3-dialogflow.googleapis.com:443",
            "asia-northeast1": "asia-northeast1-dialogflow.googleapis.com:443",
            "asia-southeast1": "asia-southeast1-dialogflow.googleapis.com:443",
            "australia-southeast1": "australia-southeast1-dialogflow.googleapis.com:443",
        }
        
        if location in region_endpoints:
            from google.api_core import client_options
            return client_options.ClientOptions(
                api_endpoint=region_endpoints[location]
            )
        return None
    
    def _initialize_vertex_ai(self):
        """Initialize Vertex AI with credentials from environment variables"""
        try:
            # Get values from environment variables
            project_id = os.getenv("GCP_PROJECT_ID")
            agent_id = os.getenv("AGENT_ID")
            agent_location = os.getenv("AGENT_LOCATION", "us-central1")
            language_code = os.getenv("LANGUAGE_CODE", "en")
            
            if not all([project_id, agent_id]):
                raise ValueError("Missing required environment variables for Vertex AI")
            
            # Get validated credentials
            credentials = self._get_credentials()
            
            # Initialize Dialogflow CX client with correct regional endpoint
            client_options = self._get_dialogflow_client_options(agent_location)
            if client_options:
                self.dialogflow_client = dialogflow.SessionsClient(
                    credentials=credentials,
                    client_options=client_options
                )
                logger.info(f"Using regional endpoint for: {agent_location}")
            else:
                self.dialogflow_client = dialogflow.SessionsClient(credentials=credentials)
                logger.info("Using default Dialogflow endpoint")
            
            # Store agent details
            self.agent_id = agent_id
            self.agent_location = agent_location
            self.project_id = project_id
            self.language_code = language_code
            
            logger.info("Vertex AI and Dialogflow CX initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing Vertex AI: {str(e)}")
            raise
    
    def _sanitize_url(self, url):
        """Sanitize and validate URLs to prevent about:blank#blocked errors"""
        if not url:
            return None
        
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        try:
            parsed = urlparse(url)
            if not parsed.netloc:
                return None
            
            sanitized_url = urlunparse((
                parsed.scheme,
                parsed.netloc,
                quote(parsed.path),
                quote(parsed.params),
                quote(parsed.query),
                quote(parsed.fragment)
            ))
            
            return sanitized_url
        except Exception:
            return None
    
    def _format_response(self, answer):
        """Format the response with proper HTML formatting and safe clickable links"""
        if not answer:
            return "No answer generated. Please try again."
        
        # Format line breaks
        formatted_answer = answer.replace('\n', '<br>')
        
        # Find and format URLs safely
        url_pattern = r'(https?://[^\s<>"\'\)]+|www\.[^\s<>"\'\)]+)'
        urls = re.findall(url_pattern, formatted_answer)
        
        for url in urls:
            sanitized_url = self._sanitize_url(url)
            if sanitized_url:
                link_html = f'<a href="{sanitized_url}" target="_blank" rel="noopener noreferrer" style="color: #1a3e8c; text-decoration: underline;">{url}</a>'
                formatted_answer = formatted_answer.replace(url, link_html)
        
        return formatted_answer
    
    def _extract_response_text(self, response):
        """Extract text response from Dialogflow CX response object"""
        try:
            logger.info("Attempting to extract response text...")
            
            # Method 1: Check response messages in query_result
            if hasattr(response, 'query_result') and response.query_result:
                logger.info("Found query_result in response")
                
                # Check response_messages
                if hasattr(response.query_result, 'response_messages') and response.query_result.response_messages:
                    logger.info(f"Found {len(response.query_result.response_messages)} response messages")
                    text_responses = []
                    for i, message in enumerate(response.query_result.response_messages):
                        logger.info(f"Message {i}: {message}")
                        if hasattr(message, 'text') and message.text:
                            text_responses.extend(message.text.text)
                            logger.info(f"Text message found: {message.text.text}")
                        elif hasattr(message, 'payload') and message.payload:
                            logger.info(f"Payload message: {message.payload}")
                    
                    if text_responses:
                        combined_text = "\n".join(text_responses)
                        logger.info(f"Combined text from response_messages: {combined_text}")
                        return combined_text
                
                # Method 2: Check fulfillment_text
                if hasattr(response.query_result, 'fulfillment_text') and response.query_result.fulfillment_text:
                    logger.info(f"Found fulfillment_text: {response.query_result.fulfillment_text}")
                    return response.query_result.fulfillment_text
            
            # Method 3: Check fulfillment_response messages
            if hasattr(response, 'query_result') and response.query_result:
                if hasattr(response.query_result, 'fulfillment_response') and response.query_result.fulfillment_response:
                    if hasattr(response.query_result.fulfillment_response, 'messages') and response.query_result.fulfillment_response.messages:
                        logger.info(f"Found {len(response.query_result.fulfillment_response.messages)} fulfillment messages")
                        text_responses = []
                        for i, message in enumerate(response.query_result.fulfillment_response.messages):
                            logger.info(f"Fulfillment message {i}: {message}")
                            if hasattr(message, 'text') and message.text:
                                text_responses.extend(message.text.text)
                                logger.info(f"Fulfillment text: {message.text.text}")
                        
                        if text_responses:
                            combined_text = "\n".join(text_responses)
                            logger.info(f"Combined text from fulfillment: {combined_text}")
                            return combined_text
            
            # Method 4: Check for custom payload or other response types
            if hasattr(response, 'query_result') and response.query_result:
                # Log intent information
                if hasattr(response.query_result, 'intent') and response.query_result.intent:
                    intent_name = response.query_result.intent.display_name
                    logger.info(f"Matched intent: {intent_name}")
                
                # Try to convert the whole response to string as last resort
                try:
                    response_str = str(response)
                    if "Pekeliling" in response_str or "pekeliling" in response_str:
                        logger.info("Found Pekeliling reference in response string")
                        # Extract relevant parts
                        lines = response_str.split('\n')
                        pekeliling_lines = [line for line in lines if 'Pekeliling' in line or 'pekeliling' in line]
                        if pekeliling_lines:
                            return "Information about Pekeliling:\n" + "\n".join(pekeliling_lines[:10])  # Limit to first 10 lines
                except:
                    pass
            
            logger.warning("No usable text response found in Dialogflow response")
            return None
            
        except Exception as e:
            logger.error(f"Error extracting response text: {str(e)}")
            return None
    
    def _call_vertex_ai_agent(self, query):
        """Call Vertex AI Agent Builder API"""
        try:
            session_id = f"session_{int(time.time())}_{hash(query) % 10000}"
            session_path = f"projects/{self.project_id}/locations/{self.agent_location}/agents/{self.agent_id}/sessions/{session_id}"
            
            logger.info(f"Query to Vertex AI: {query}")
            logger.info(f"Session path: {session_path}")
            
            # Create text input
            text_input = dialogflow.TextInput(text=query)
            query_input = dialogflow.QueryInput(
                text=text_input, 
                language_code=self.language_code
            )
            
            # Create request
            request = dialogflow.DetectIntentRequest(
                session=session_path,
                query_input=query_input,
            )
            
            # Make API call with timeout
            logger.info("Sending request to Dialogflow CX...")
            response = self.dialogflow_client.detect_intent(
                request=request,
                timeout=30.0
            )
            
            logger.info("Received response from Dialogflow CX")
            
            # Extract response text using multiple methods
            answer = self._extract_response_text(response)
            
            if answer:
                logger.info(f"Successfully extracted answer: {answer[:200]}...")  # Log first 200 chars
                return answer
            else:
                logger.warning("No response text could be extracted from Dialogflow")
                
                # Provide more specific fallback based on the query
                if "pekeliling" in query.lower():
                    return "I understand you're asking about Pekeliling documents. However, I'm currently unable to retrieve the specific Pekeliling information from our knowledge base. Please try rephrasing your question or contact MQA directly for the most up-to-date Pekeliling documents."
                else:
                    return "I couldn't generate a proper response for your query. Please try rephrasing or ask about a different topic."
            
        except GoogleAPICallError as e:
            logger.error(f"Google API call error: {str(e)}")
            return "Sorry, I encountered an error with the AI service. Please try again in a moment."
        except Exception as e:
            logger.error(f"Error calling Vertex AI Agent: {str(e)}")
            logger.exception("Full traceback:")
            return "Sorry, I encountered an error processing your request. Please try again."
    
    def chat(self, query: str):
        """
        Process user query using Vertex AI Agent Builder
        """
        try:
            # Validate input
            if not query or not query.strip():
                return {
                    "answer": "Please provide a valid question or message.",
                    "sources": []
                }
            
            # Call Vertex AI Agent Builder
            answer = self._call_vertex_ai_agent(query)
            
            # Format the response
            if not answer or answer.strip() == '':
                formatted_answer = "I couldn't find specific information about this. Please try rephrasing your question."
            else:
                formatted_answer = self._format_response(answer)
            
            return {
                "answer": formatted_answer,
                "sources": []
            }
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            logger.exception("Full traceback:")
            return {
                "answer": "Sorry, I encountered an error processing your request. Please try again.",
                "sources": []
            }