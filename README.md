# 🤖 Dynamic Company Services Chatbot

This project implements a conversational AI chatbot designed to provide information about **other companies' services**. It achieves this by dynamically searching the web, processing the retrieved content, and synthesizing answers using a Large Language Model (LLM). The chatbot is built with conversational memory to handle follow-up questions and provides natural responses to basic greetings.

## ✨ Key Features

* **Dynamic Web Search:** Fetches real-time information using the Google Custom Search JSON API.
* **Retrieval-Augmented Generation (RAG):** Uses LangChain to build an in-memory vector database from fetched web snippets, ensuring factual accuracy.
* **Conversational Memory:** The LLM considers previous turns in the conversation for coherent responses.
* **LLM-driven Entity Extraction:** Intelligently extracts company names and service keywords from user queries.
* **Greeting/Chit-chat Handling:** Provides pre-defined, direct responses for casual interactions.
* **Streamlit UI:** An interactive and user-friendly web interface.
* **Modular Design & Unit Testing:** Organized code with tests for individual components.
* **Continuous Integration (CI):** Automates testing using GitHub Actions.

## 📐 Architecture Overview

The chatbot's core functionality is orchestrated through a Retrieval-Augmented Generation (RAG) architecture:


## ⚙️ Setup (Local Development)

This section guides you through setting up the chatbot on your local machine.

### 1. Create Your Project Directory and Structure

Create the main project folder and the necessary subdirectories:

```bash
mkdir dynamic_company_chatbot
cd dynamic_company_chatbot
mkdir tests
mkdir .github
mkdir .github/workflows

pip install streamlit langchain langchain-google-genai python-dotenv requests google-api-python-client chromadb unstructured beautifulsoup4 pytest pytest-mock
```

### 4\. Google Custom Search Engine (CSE) Setup - **Crucial Step**

This step configures the mechanism for your chatbot to search the public web for company information.

1.  **Go to the Google Programmable Search Engine control panel:**
    [https://programmablesearchengine.google.com/controlpanel/all](https://programmablesearchengine.google.com/controlpanel/all)
    (Ensure you are logged into your Google account.)

2.  Click the **"Add new search engine"** button.

3.  **Configure "Sites to search":**

      * **Crucially, specify reputable domains** that are likely to contain reliable information about companies and their services. This acts as a "pre-filter" for your RAG system, making searches more focused.
      * **Recommended domains to add:** `wikipedia.org`, `crunchbase.com`, `forbes.com`, reputable industry news sites (e.g., `techcrunch.com`), major business news outlets (e.g., `reuters.com`, `bloomberg.com`), and relevant software/service review sites (e.g., `g2.com`, `capterra.com`). You can also include `*.com` or `*.org` for broader searches, but this may yield more varied results.
      * You can also add specific official company websites if you anticipate frequent queries about them (e.g., `microsoft.com/cloud`, `salesforce.com/crm`).

4.  Give your CSE a **name** (e.g., "Company Services Search").

5.  Click **"Create."**

6.  **Obtain your Search Engine ID (CX ID):**

      * After creation, you'll see a script snippet (e.g., `<script async src="https://cse.google.com/cse.js?cx=52288af5c0e474764"></script>`). The `cx` value in this script is your **Search Engine ID**. Copy this value; it will be used as `GOOGLE_CSE_ID`.

7.  **Enable the Custom Search JSON API and get your Google Cloud API Key:**

      * In the Google Programmable Search Engine control panel, go to the **"API"** tab.
      * Click on the link to **"Get a key"** or navigate directly to the [Google Cloud Console](https://console.cloud.google.com/).
      * In the Google Cloud Console, ensure you're in the **same Google Cloud project** that is linked to your CSE (or create a new one).
      * Go to **"APIs & Services" \> "Credentials."**
      * Click **"+ CREATE CREDENTIALS"** and choose **"API Key."**
      * A new API key will be generated. Copy this key.
      * **Security Best Practice:** After creating the key, **RESTRICT THE KEY**. Click on the key name, then select **"Restrict key."** Choose "Restrict API key" and from the dropdown, select **"Custom Search API."** This ensures this API key can only be used for Google Custom Search, significantly enhancing security.
      * This API key will be used as your `GOOGLE_API_KEY_FOR_SEARCH`.

### 5\. API Key Configuration (`.env` file)

Populate the `.env` file you created in step 1 with your API keys. **Replace the placeholder values with your actual keys.**

**Important:** **Never commit this `.env` file to version control (Git).** The `.gitignore` file already includes this.

### 6\. Populate Code Files

Copy the provided Python code into their respective empty files (`app.py`, `external_info_retriever.py`, `llm_rag_service.py`, `requirements.txt`, `tests/__init__.py`, `tests/test_external_info_retriever.py`, `tests/test_llm_rag_service.py`, `.github/workflows/ci.yml`).

## 🚀 Running the Application (Local)

Once all setup and file population are complete:

1.  **Activate your Python virtual environment** (if not already active).
2.  **Navigate to your project's root directory** in your terminal.
3.  **Run the Streamlit application:**
    ```bash
    streamlit run app.py
    ```
4.  Your default web browser should open a new tab displaying the chatbot interface.

## 🧪 Testing (Local)

The project includes unit tests for the core logic modules to ensure their functionality and stability.

1.  **Activate your Python virtual environment** (if not already active).
2.  **Navigate to your project's root directory** in your terminal.
3.  **Run the tests using Pytest:**
    ```bash
    pytest -v -s
    ```
      * `-v`: Provides more verbose output, showing individual test results.
      * `-s`: Prevents pytest from capturing stdout/stderr, allowing you to see `print()` statements from your code (useful for debugging).
4.  All tests should pass.

## 🚢 Deployment (Streamlit Community Cloud)

You can deploy this chatbot to a public web address using Streamlit Community Cloud.

### Prerequisites

  * A GitHub account.
  * Your project code pushed to a GitHub repository.

### Steps

1.  **Create a GitHub Repository:**

      * Go to [GitHub](https://github.com/) and log in.
      * Click the green "New" button (or `+` -\> "New repository").
      * Give your repository a name (e.g., `dynamic-company-chatbot`).
      * Choose if it's public or private.
      * Click "Create repository."

2.  **Push Your Code to GitHub:**

      * Open your terminal, navigate to your project's root directory (`dynamic_company_chatbot`).
      * Initialize Git:
        ```bash
        git init
        ```
      * Add all your files (excluding `.env`, which is ignored by `.gitignore`):
        ```bash
        git add .
        ```
      * Commit your changes:
        ```bash
        git commit -m "Initial commit: Dynamic Company Services Chatbot"
        ```
      * Add the remote GitHub repository:
        ```bash
        git remote add origin [https://github.com/YOUR_GITHUB_USERNAME/dynamic-company-chatbot.git](https://github.com/YOUR_GITHUB_USERNAME/dynamic-company-chatbot.git)
        ```
        (Replace `YOUR_GITHUB_USERNAME` and `dynamic-company-chatbot` with your actual values)
      * Set the default branch (optional, but good practice):
        ```bash
        git branch -M main
        ```
      * Push your code to GitHub:
        ```bash
        git push -u origin main
        ```
      * Verify that all your project files (including `requirements.txt` and the `.github/workflows/ci.yml` CI configuration) are visible on your GitHub repository.

3.  **Add Secrets to GitHub Repository (CRITICAL FOR API KEYS):**

      * Go to your GitHub repository on the web.
      * Navigate to **Settings \> Secrets and variables \> Actions**.
      * Click "New repository secret."
      * Add the following secrets, using your *actual* API keys as values (these correspond to the variables in your `.env` file):
          * **Name:** `GOOGLE_API_KEY`
          * **Value:** `YOUR_GOOGLE_GEMINI_API_KEY`
          * **Name:** `GOOGLE_CSE_ID`
          * **Value:** `YOUR_SEARCH_ENGINE_ID_FROM_STEP_4`
          * **Name:** `GOOGLE_API_KEY_FOR_SEARCH`
          * **Value:** `YOUR_GOOGLE_CLOUD_API_KEY_FROM_STEP_4`
      * These secrets will be securely available to your deployed Streamlit app as environment variables.

4.  **Deploy on Streamlit Community Cloud:**

      * Go to [Streamlit Community Cloud](https://share.streamlit.io/) and log in (you can sign in with your GitHub account).
      * Click "New app" in the top right corner.
      * Select "From existing repo."
      * **Connect your GitHub account** if you haven't already.
      * Fill in the deployment details:
          * **Repository:** Select your `dynamic-company-chatbot` repository.
          * **Branch:** `main` (or the branch where your code resides).
          * **Main file path:** `app.py` (the path to your primary Streamlit script).
          * **Python version:** Choose a compatible Python version (e.g., 3.10, 3.11).
      * **Advanced settings:** Ensure your secrets are correctly linked (they usually auto-detect if you set them up in GitHub).
      * Click "Deploy\!"

Streamlit will now build and deploy your application. This may take a few minutes for the initial deployment. Once complete, you'll receive a public URL for your chatbot. Any future pushes to the specified branch on GitHub will automatically trigger a new deployment.

## 📝 Developer Hiring Test - Question 2 Answers

### Q2: Design a basic chatbot that helps users get quick answers about a company's services using an LLM.

#### a. 2-3 key things the chatbot should be able to help users with:

1.  **Service Offerings:** Provide detailed descriptions of various services offered by a specific company (e.g., "What cloud services does Google offer?").
2.  **Pricing/Plans (General):** Give information on general pricing structures or tiers if available (e.g., "What are Salesforce's CRM pricing plans?").
3.  **Contact/Support Information:** Direct users to appropriate contact channels for a company's services (e.g., "How can I contact Microsoft support for their software?").
4.  **Basic FAQs:** Answer common questions about a company's general operations related to its services (e.g., "What are the benefits of using Amazon Web Services?").

#### b. Basic plan to build it:

1.  **Intent and Entity Extraction:** Use an LLM to identify the user's core intent (e.g., "ask about services," "find pricing") and extract key entities (e.g., company name, specific service keywords).
2.  **Information Retrieval (RAG):**
      * For external company services, leverage a web search API (like Google Custom Search) to dynamically retrieve relevant information from public sources.
      * Convert this retrieved text into LangChain `Document` objects.
      * Create a temporary, in-memory vector database (e.g., ChromaDB) from these documents and their embeddings.
      * Implement a LangChain RAG chain to select the most relevant document chunks based on the user's query.
3.  **Answer Generation:** Pass the user's query, the retrieved context (documents), and the chat history to a powerful LLM (e.g., Google Gemini Pro Flash) to synthesize a coherent and factual answer.
4.  **Conversational Memory:** Maintain chat history and pass it to the LLM to enable context-aware responses for follow-up questions.
5.  **User Interface:** Develop a simple chat interface using Streamlit.
6.  **Deployment:** Deploy the application to a cloud platform like Streamlit Community Cloud.

#### c. Tools or platforms might you use:

  * **Programming Language:** Python
  * **LLM Framework:** LangChain
  * **LLM:** Google Gemini API (`gemini-pro-flash`, `models/embedding-001`)
  * **Vector Database:** ChromaDB (for in-memory dynamic RAG)
  * **Web Search API:** Google Custom Search JSON API
  * **UI Framework:** Streamlit
  * **Dependency Management:** `pip`, `venv`
  * **API Key Management:** `python-dotenv` (local), GitHub Secrets (deployment)
  * **Testing:** `pytest`, `pytest-mock`
  * **Version Control:** Git, GitHub
  * **CI/CD:** GitHub Actions
  * **Deployment Platform:** Streamlit Community Cloud

#### d. Would you use an existing chatbot builder, connect to an API, or something else?

I would primarily **connect to APIs** (specifically LLM APIs and web search APIs) rather than using a rigid "existing chatbot builder."

  * **Connecting to APIs (Chosen Approach):** This provides maximum flexibility and customization. It allows for a tailored RAG pipeline, custom entity extraction, and integration with dynamic, real-time data sources. It gives full control over the user experience and the underlying logic.
  * **Why not just an existing chatbot builder:** While builders (like Dialogflow, Rasa, IBM Watson Assistant) offer quick setup for rule-based or intent-driven chatbots, they often limit flexibility for advanced RAG patterns, custom data sources (beyond predefined integrations), or dynamic web searches. Integrating an LLM with these can still be done, but a custom API-driven approach provides more granular control for complex, real-time information retrieval about external entities.

#### e. How would you make sure the chatbot gives helpful and safe answers?

1.  **Retrieval-Augmented Generation (RAG):** Ensure answers are grounded in retrieved facts from reputable sources, not solely on the LLM's training data. This significantly reduces "hallucinations."
2.  **Prompt Engineering:** Design clear and strict system prompts for the LLM that instruct it to:
      * "Only use the provided context."
      * "State if the information is not available in the context."
      * "Do not make up facts."
      * Define its persona as helpful and factual.
3.  **Content Filtering (Pre-LLM):** Filter retrieved content (e.g., remove offensive or irrelevant snippets) before passing it to the LLM.
4.  **Safety Filters (LLM API):** Utilize built-in safety features and content moderation APIs provided by the LLM provider (e.g., Google Gemini's safety settings) to detect and block harmful content.
5.  **Handling Out-of-Scope Queries:** Implement logic to detect when a query is outside the chatbot's domain (e.g., asking for medical advice) and gracefully decline to answer or redirect the user.

#### f. 2-3 steps you'd take to make sure the chatbot doesn't say anything wrong or confusing:

1.  **Curated Search Sources:** For factual queries, configure the Google Custom Search Engine to prioritize highly reputable and relevant websites. Avoid overly broad or unreliable sources.
2.  **Strict Prompting for Non-Hallucination:** Reinforce LLM instructions to explicitly state when it doesn't have the information based on the provided context, rather than attempting to guess or invent an answer.
3.  **Iterative Testing and User Feedback:** Continuously test the chatbot with diverse and challenging queries. Implement a feedback mechanism (e.g., "Was this answer helpful?") to identify and correct instances where the chatbot provides incorrect or confusing information. Use these problematic interactions to refine prompts, improve retrieval, or add specific rules.
4.  **Clear Scope Communication:** Set user expectations upfront about the chatbot's capabilities and limitations (e.g., "I can answer questions about companies' services, but not personal advice.").

#### g. What would you need to learn or research before starting this project?

1.  **LLM Concepts:** Understanding of prompt engineering, RAG architecture, LLM limitations (hallucinations, token limits), and conversational AI principles.
2.  **LangChain Framework:** How to build chains, use various components (loaders, text splitters, retrievers, prompts, LLMs), and manage conversational history.
3.  **Vector Databases:** Basics of how embeddings work, how vector databases store and retrieve information, and specifically how to use ChromaDB (or other chosen vector stores).
4.  **Google API Ecosystem:** How to set up Google Cloud projects, generate and manage API keys, and specifically use the Google Custom Search JSON API and Google Gemini API.
5.  **Streamlit:** How to build interactive web applications and manage session state.
6.  **Web Scraping/Data Extraction Best Practices:** Legal and ethical considerations, how to interact with websites programmatically (even just for snippets), and potential anti-bot measures.
7.  **CI/CD Basics:** Understanding of GitHub Actions workflows and how to automate testing and deployment.

#### h. 2-3 topics or questions you'd want to explore to build this properly:

1.  **Optimal Search Query Formulation:** How to programmatically generate the most effective and precise search queries for the Google Custom Search API based on extracted entities, to maximize retrieval of relevant snippets.
2.  **Advanced Document Chunking/Re-ranking:** Techniques to further refine the retrieved web snippets for better LLM consumption (e.g., re-ranking retrieved documents based on relevance score or keyword density before passing to LLM).
3.  **Entity Resolution/Disambiguation:** How to handle ambiguous company names (e.g., "Apple" - tech vs. music) or services that might share names across industries, possibly by prompting the user for clarification.
4.  **Scalability & Cost Optimization:** Strategies for managing API costs and ensuring performance as user load increases (e.g., advanced caching mechanisms, API rate limit handling, choosing appropriate LLM models for different tasks).
5.  **Feedback Loop for Improvement:** How to build an automated (or semi-automated) system to collect user feedback on answer quality and use it to improve the LLM's prompts or retrieval logic over time.

<!-- end list -->
