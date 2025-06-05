# app.py
"""
This is the Streamlit UI and orchestrator. It includes a preliminary LLM call 
to extract company name and service keywords.
"""
import streamlit as st
import asyncio
import os
import json
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage
from typing import Tuple, Optional, List

# Import your service modules
import external_info_retriever
import llm_rag_service

# Load environment variables from .env file (for local development)
load_dotenv()

# --- Configuration ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    st.error("Google Gemini API key not found. Please set it in your .env file or GitHub Secrets.")
    st.stop() # Stop the app if API key is missing

# --- LLM for Extraction (Lightweight Model) ---
extraction_llm = ChatGoogleGenerativeAI(model="models/gemini-1.5-flash", google_api_key=GOOGLE_API_KEY, temperature=0.1)

# Prompt for extraction - Modified to include specific tags for greetings/chit-chat
extraction_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are an expert entity extractor. Your task is to identify the company name "
     "and the specific service-related keywords from a user's query. "
     "Respond ONLY in JSON format with two fields: 'company_name' and 'service_keywords'. "
     "If a company name or service is not clearly specified, use null for that field. "
     "If the user query is a simple greeting (e.g., 'hi', 'hello', 'how are you?', 'good morning'), "
     "set both 'company_name' and 'service_keywords' to 'GREETING'. "
     "If the user query is a simple acknowledgement or thank you (e.g., 'thank you', 'ok', 'got it', 'bye'), "
     "set both 'company_name' and 'service_keywords' to 'CHITCHAT'. "
     "Example 1: User: 'What are Microsoft's cloud offerings?' -> Output: "
     "```json\n{{\"company_name\": \"Microsoft\", \"service_keywords\": \"cloud offerings\"}}\n```"
     "Example 2: User: 'Hi there!' -> Output: "
     "```json\n{{\"company_name\": \"GREETING\", \"service_keywords\": \"GREETING\"}}\n```"
     "Example 3: User: 'Thank you!' -> Output: "
     "```json\n{{\"company_name\": \"CHITCHAT\", \"service_keywords\": \"CHITCHAT\"}}\n```"
    ),
    ("human", "{query}")
])
extraction_chain = extraction_prompt | extraction_llm | StrOutputParser()

async def extract_query_entities(query: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Uses an LLM to extract company name and service keywords from a user query,
    or identify it as a greeting/chit-chat.
    """
    try:
        json_str = await extraction_chain.ainvoke({"query": query})
        json_str = json_str.strip().replace("```json\n", "").replace("\n```", "")
        entities = json.loads(json_str)
        company_name = entities.get("company_name")
        service_keywords = entities.get("service_keywords")
        return company_name, service_keywords
    except json.JSONDecodeError as e:
        st.warning(f"Could not parse entity extraction response: {json_str}. Error: {e}")
        return None, None
    except Exception as e:
        st.error(f"Error during entity extraction: {e}")
        return None, None

# --- Streamlit App Layout ---
st.set_page_config(page_title="Dynamic Company Services Chatbot", layout="centered")

st.title("🤖 Dynamic Company Services Chatbot")
st.markdown("Ask me anything about other companies' services (e.g., 'What are Google's cloud services?', 'Tell me about Salesforce's CRM features').")

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Function to format Streamlit chat history for LangChain ---
def get_langchain_chat_history() -> List[HumanMessage | AIMessage]:
    """
    Converts Streamlit's session state messages into LangChain's HumanMessage/AIMessage format.
    """
    langchain_messages = []
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            langchain_messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            langchain_messages.append(AIMessage(content=msg["content"]))
    return langchain_messages

# User input
if prompt := st.chat_input("How can I help you today?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Searching and thinking..."):
            current_langchain_chat_history = get_langchain_chat_history()
            
            # Step 1: Extract query entities (or identify as greeting/chit-chat)
            company_name, service_keywords = asyncio.run(extract_query_entities(prompt))

            llm_response = ""

            # --- Handle Greetings and Chit-chat First ---
            if company_name == "GREETING" and service_keywords == "GREETING":
                llm_response = "Hello there! How can I assist you with company services today?"
            elif company_name == "CHITCHAT" and service_keywords == "CHITCHAT":
                llm_response = "You're welcome! Is there anything specific about company services you'd like to know?"
            elif company_name and service_keywords: # Proceed with RAG if company and service are found
                st.info(f"Searching for: Company='{company_name}', Services='{service_keywords}'")
                
                # Step 2: Fetch external content based on extracted entities
                external_documents = asyncio.run(external_info_retriever.get_company_web_content(company_name, service_keywords))
                
                if external_documents:
                    st.success(f"Found {len(external_documents)} relevant snippets. Generating answer...")
                    # Step 3: Get RAG answer from LLM using fetched documents and chat history
                    llm_response = asyncio.run(llm_rag_service.get_rag_answer(
                        prompt, # Current user question
                        external_documents,
                        current_langchain_chat_history # Pass the full history
                    ))
                else:
                    llm_response = "I couldn't find specific information for that company and service on the web. Could you please rephrase or provide more details?"
            elif company_name:
                # If only company name is extracted, but no specific service keywords
                llm_response = f"I can look up information about {company_name}. What specific services or aspects are you interested in?"
            else:
                # If neither company nor service keywords are clear (and not a greeting/chit-chat)
                llm_response = "I couldn't identify a specific company or service in your query. Please ask about a company's services (e.g., 'What are Google's cloud services?')."

            st.markdown(llm_response)
            st.session_state.messages.append({"role": "assistant", "content": llm_response})

