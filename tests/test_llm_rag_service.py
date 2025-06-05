# tests/test_llm_rag_service.py
import pytest
from unittest.mock import MagicMock
from langchain_core.documents import Document
import llm_rag_service # Import the module to be tested
import os

# Mock environment variables for testing
@pytest.fixture(autouse=True)
def mock_env_vars(mocker):
    mocker.patch.dict(os.environ, {
        "GOOGLE_API_KEY": "mock_gemini_api_key"
    })
    # Reload module to pick up mocked env vars if it was loaded before fixture
    import importlib
    importlib.reload(llm_rag_service)

@pytest.mark.asyncio
async def test_get_rag_answer_with_relevant_docs(mocker):
    """
    Tests RAG answer generation when relevant documents are provided.
    Mocks LLM and embeddings.
    """
    # Mock GoogleGenerativeAIEmbeddings
    mock_embeddings_cls = mocker.patch('llm_rag_service.GoogleGenerativeAIEmbeddings')
    mock_embeddings_instance = MagicMock()
    mock_embeddings_cls.return_value = mock_embeddings_instance
    mock_embeddings_instance.embed_documents.return_value = [[0.1]*768, [0.2]*768] # Dummy embeddings

    # Mock ChatGoogleGenerativeAI (the LLM)
    mock_llm_cls = mocker.patch('llm_rag_service.ChatGoogleGenerativeAI')
    mock_llm_instance = MagicMock()
    mock_llm_cls.return_value = mock_llm_instance
    # Mock the invoke method of the LLM instance to return a predefined answer
    mock_llm_instance.invoke.return_value = "Based on the provided context, Company A offers excellent cloud services."

    # Dummy documents to simulate retrieved content
    dummy_docs = [
        Document(page_content="Company A is a leading provider of cloud services including SaaS and PaaS.", metadata={"source": "doc1"}),
        Document(page_content="Their cloud services are known for high availability and scalability.", metadata={"source": "doc2"})
    ]
    user_question = "What cloud services does Company A offer?"

    answer = await llm_rag_service.get_rag_answer(user_question, dummy_docs)

    # Assertions
    assert "Company A offers excellent cloud services" in answer
    mock_embeddings_cls.assert_called_once_with(model="models/embedding-001", google_api_key="mock_gemini_api_key")
    mock_llm_cls.assert_called_once_with(model="gemini-pro", google_api_key="mock_gemini_api_key", temperature=0.2)
    # You could also assert that the LLM's invoke method was called with a prompt containing the dummy_docs content

@pytest.mark.asyncio
async def test_get_rag_answer_no_documents(mocker):
    """
    Tests RAG answer generation when no external documents are provided.
    """
    # No need to mock LLM/embeddings if no documents are passed, as it should return early.
    user_question = "What services does Company Z provide?"
    external_documents = [] # Empty list of documents

    answer = await llm_rag_service.get_rag_answer(user_question, external_documents)

    assert "couldn't find enough relevant information" in answer
    # Ensure LLM and embeddings were NOT called
    mocker.patch('llm_rag_service.GoogleGenerativeAIEmbeddings', side_effect=AssertionError("Embeddings should not be called"))
    mocker.patch('llm_rag_service.ChatGoogleGenerativeAI', side_effect=AssertionError("LLM should not be called"))


@pytest.mark.asyncio
async def test_get_rag_answer_llm_api_error(mocker):
    """
    Tests error handling when the LLM API call fails.
    """
    mocker.patch('llm_rag_service.GoogleGenerativeAIEmbeddings') # Still need to mock embeddings for vectorstore creation

    mock_llm_cls = mocker.patch('llm_rag_service.ChatGoogleGenerativeAI')
    mock_llm_instance = MagicMock()
    # Simulate an error during LLM invocation
    mock_llm_instance.invoke.side_effect = Exception("LLM API connection failed")
    mock_llm_cls.return_value = mock_llm_instance

    dummy_docs = [Document(page_content="Some content.", metadata={})]
    user_question = "Test question."

    answer = await llm_rag_service.get_rag_answer(user_question, dummy_docs)

    assert "internal error" in answer

@pytest.mark.asyncio
async def test_get_rag_answer_missing_api_key(mocker):
    """
    Tests behavior when LLM API key is missing.
    """
    mocker.patch.dict(os.environ, clear=True) # Clear env vars for this test
    # Reload module to pick up cleared env vars
    import importlib
    importlib.reload(llm_rag_service)

    user_question = "What services?"
    dummy_docs = [Document(page_content="Some content.", metadata={})]

    answer = await llm_rag_service.get_rag_answer(user_question, dummy_docs)
    assert "core AI capabilities are not configured" in answer