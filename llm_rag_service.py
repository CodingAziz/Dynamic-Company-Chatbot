# llm_rag_service.py
"""
This module handles the dynamic RAG process using an in-memory ChromaDB and the Gemini LLM.
"""
import os
from typing import List
from langchain_core.documents import Document
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain # Removed create_history_aware_retriever
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage
import traceback

# Load environment variables (for local development and testing)
from dotenv import load_dotenv
load_dotenv()

# --- Configuration ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    print("WARNING: Google Gemini API key not set. LLM interaction will not function.")

# --- RAG Answer Generation Function ---
async def get_rag_answer(user_question: str, external_documents: List[Document], chat_history: List[HumanMessage | AIMessage]) -> str:
    """
    Generates an answer using Retrieval-Augmented Generation (RAG).
    It creates an in-memory vector store from provided documents, retrieves relevant
    chunks (based on current question only), and uses them as context for the Google Gemini LLM.

    Args:
        user_question (str): The user's current question.
        external_documents (List[Document]): A list of LangChain Document objects
                                            (e.g., search snippets from external_info_retriever).
        chat_history (List[HumanMessage | AIMessage]): A list of LangChain message objects
                                    representing the conversation history.

    Returns:
        str: The LLM's generated answer based on the provided context.
             Returns a fallback message if no documents are provided or an error occurs.
    """
    if not GOOGLE_API_KEY:
        return "I'm sorry, my core AI capabilities are not configured. Please check the API key."

    if not external_documents:
        return "I couldn't find enough relevant information on the web to answer that specific query. Please try rephrasing or asking about a different company/service."

    try:
        # 1. Initialize Embeddings Model
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=GOOGLE_API_KEY)

        # 2. Create In-Memory ChromaDB from the provided documents
        vectorstore = Chroma.from_documents(documents=external_documents, embedding=embeddings)

        # 3. Initialize LLM (Gemini Pro Flash)
        llm = ChatGoogleGenerativeAI(model="models/gemini-1.5-flash", google_api_key=GOOGLE_API_KEY, temperature=0.2)

        # --- No History-Aware Retriever ---
        # The retriever will search the in-memory vector store for the most relevant
        # document chunks based *only* on the `user_question` provided to `invoke`.
        retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

        # --- Answer Generation Chain with Retrieved Docs and Original Question ---
        # The qa_prompt still includes MessagesPlaceholder for chat_history.
        # This allows the final LLM call to be aware of the full conversation flow,
        # even if the retrieval step itself doesn't use the history for reformulation.
        qa_prompt = ChatPromptTemplate.from_messages([
            ("system",
             "You are an AI assistant specializing in providing information about various companies' services. "
             "Use the following 'SEARCH RESULTS' to answer the user's question accurately and concisely. "
             "Focus only on the information provided in the 'SEARCH RESULTS'. "
             "If the 'SEARCH RESULTS' do not contain the answer, state clearly that you cannot find the answer "
             "based on the provided information. Do not make up any details. "
             "If the user asks for contact information, provide it if available in the search results, otherwise state it's not available."
             "\n\nSEARCH RESULTS:\n{context}"),
            MessagesPlaceholder("chat_history"), # Still include for conversational awareness in LLM response generation
            ("human", "{input}"), # The original user's question
        ])
        document_chain = create_stuff_documents_chain(llm, qa_prompt)

        # --- Combined Conversational RAG Chain ---
        # This chain directly uses the base retriever.
        retrieval_chain = create_retrieval_chain(retriever, document_chain)

        # 8. Invoke the Chain with the User's Question and Chat History
        # 'input' is the current question that both the retriever and LLM will see.
        # 'chat_history' is only passed to the LLM within document_chain for conversational context.
        response = retrieval_chain.invoke({"input": user_question, "chat_history": chat_history})

        return response.get("answer", "I couldn't generate an answer based on the retrieved information.")

    except Exception as e:
        print(f"An error occurred during RAG processing: {e}")
        traceback.print_exc()
        return "I'm sorry, I encountered an internal error while trying to process your request."

