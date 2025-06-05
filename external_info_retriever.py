# external_info_retriever.py
"""
This module handles fetching search results from Google Custom Search and processing them
into LangChain Document objects.
"""
import os
import requests
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from langchain_core.documents import Document
from typing import List

# Load environment variables from .env file (for local development)
from dotenv import load_dotenv
load_dotenv()

# --- Configuration ---
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")
GOOGLE_API_KEY_FOR_SEARCH = os.getenv("GOOGLE_API_KEY_FOR_SEARCH")
print("[DEBUG] GOOGLE_CSE_ID:", os.getenv("GOOGLE_CSE_ID"))
print("[DEBUG] GOOGLE_API_KEY_FOR_SEARCH:", os.getenv("GOOGLE_API_KEY_FOR_SEARCH"))

if not GOOGLE_CSE_ID or not GOOGLE_API_KEY_FOR_SEARCH:
    print("WARNING: Google Custom Search API keys not set. External search will not function.")

# --- External Search Function ---
async def get_company_web_content(company_name: str, service_keywords: str) -> List[Document]:
    """
    Searches Google Custom Search for information about a company's services
    and returns relevant snippets as LangChain Document objects.

    Args:
        company_name (str): The name of the company to search for.
        service_keywords (str): Keywords related to the services being inquired about.

    Returns:
        List[Document]: A list of LangChain Document objects, each containing a search snippet
                        and metadata (source URL, title, company). Returns an empty list
                        if no relevant results are found or an error occurs.
    """
    if not GOOGLE_CSE_ID or not GOOGLE_API_KEY_FOR_SEARCH:
        print("Error: Google Custom Search API keys are not configured.")
        return []

    search_query = f"{company_name} {service_keywords} services reviews official site"

    try:
        service = build("customsearch", "v1", developerKey=GOOGLE_API_KEY_FOR_SEARCH)
        response = service.cse().list(q=search_query, cx=GOOGLE_CSE_ID, num=5).execute()

        documents = []
        if 'items' in response:
            for item in response['items']:
                title = item.get('title', 'No Title')
                snippet = item.get('snippet', 'No Snippet')
                link = item.get('link', 'No Link')

                doc = Document(
                    page_content=snippet,
                    metadata={
                        "source": link,
                        "title": title,
                        "company": company_name,
                        "search_query": search_query
                    }
                )
                documents.append(doc)
        return documents

    except HttpError as e:
        print(f"Google Custom Search API Error: {e}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred during web content retrieval: {e}")
        return []

# Optional: Fetch full HTML page content (not used in async pipeline currently)
async def _fetch_full_page_content(url: str) -> str:
    """
    Fetches the full text content from a given URL using requests and BeautifulSoup.
    Consider using only if snippet-based RAG is insufficient.
    """
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        main_content = soup.find('body')

        if main_content:
            for script_or_style in main_content(['script', 'style']):
                script_or_style.decompose()
            return main_content.get_text(separator=' ', strip=True)

        return soup.get_text(separator=' ', strip=True)

    except requests.exceptions.RequestException as e:
        print(f"Error fetching full page content from {url}: {e}")
        return ""
    except Exception as e:
        print(f"Error parsing HTML from {url}: {e}")
        return ""
