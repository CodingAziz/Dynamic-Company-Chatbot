# tests/test_external_info_retriever.py
import os
import pytest
from unittest.mock import MagicMock
from langchain_core.documents import Document
import external_info_retriever # Import the module to be tested

# Mock environment variables for testing
@pytest.fixture(autouse=True)
def mock_env_vars(mocker):
    mocker.patch.dict(os.environ, {
        "GOOGLE_CSE_ID": "mock_cse_id",
        "GOOGLE_API_KEY_FOR_SEARCH": "mock_api_key_for_search"
    })
    # Reload module to pick up mocked env vars if it was loaded before fixture
    import importlib
    importlib.reload(external_info_retriever)


@pytest.mark.asyncio
async def test_get_company_web_content_success(mocker):
    """
    Tests successful retrieval of web content from Google Custom Search.
    Mocks the googleapiclient.discovery.build and its subsequent calls.
    """
    # Mock the entire googleapiclient.discovery.build call chain
    mock_build = mocker.patch('googleapiclient.discovery.build')
    mock_execute = MagicMock() # Mock the .execute() method
    mock_execute.execute.return_value = {
        'items': [
            {'title': 'CompanyX Cloud Services', 'snippet': 'Details about CompanyX cloud.', 'link': 'http://companyx.com/cloud'},
            {'title': 'CompanyX Support Plans', 'snippet': 'Information on support tiers.', 'link': 'http://companyx.com/support'}
        ]
    }
    # Set up the return values for the nested calls
    mock_build.return_value.cse.return_value.list.return_value = mock_execute

    company = "CompanyX"
    keywords = "cloud services"
    documents = await external_info_retriever.get_company_web_content(company, keywords)

    # Assertions
    assert isinstance(documents, list)
    assert len(documents) == 2
    assert all(isinstance(doc, Document) for doc in documents)

    # Verify content and metadata of the first document
    assert documents[0].page_content == 'Details about CompanyX cloud.'
    assert documents[0].metadata['source'] == 'http://companyx.com/cloud'
    assert documents[0].metadata['title'] == 'CompanyX Cloud Services'
    assert documents[0].metadata['company'] == company
    assert documents[0].metadata['search_query'] == f"{company} {keywords} services reviews official site"

    # Verify that the build and list methods were called with correct arguments
    mock_build.assert_called_once_with("customsearch", "v1", developerKey="mock_api_key_for_search")
    mock_build.return_value.cse.return_value.list.assert_called_once_with(
        q=f"{company} {keywords} services reviews official site",
        cx="mock_cse_id",
        num=5
    )

@pytest.mark.asyncio
async def test_get_company_web_content_no_results(mocker):
    """
    Tests when Google Custom Search returns no results.
    """
    mock_build = mocker.patch('googleapiclient.discovery.build')
    mock_execute = MagicMock()
    mock_execute.execute.return_value = {'items': []} # Empty items list
    mock_build.return_value.cse.return_value.list.return_value = mock_execute

    documents = await external_info_retriever.get_company_web_content("NonExistentCompany", "services")
    assert isinstance(documents, list)
    assert len(documents) == 0

@pytest.mark.asyncio
async def test_get_company_web_content_api_error(mocker):
    """
    Tests error handling when Google Custom Search API raises an HttpError.
    """
    from googleapiclient.errors import HttpError
    mock_build = mocker.patch('googleapiclient.discovery.build')
    mock_execute = MagicMock()
    # Simulate an HTTP error response
    mock_execute.execute.side_effect = HttpError(MagicMock(status=403), b'Forbidden')
    mock_build.return_value.cse.return_value.list.return_value = mock_execute

    documents = await external_info_retriever.get_company_web_content("CompanyA", "services")
    assert isinstance(documents, list)
    assert len(documents) == 0 # Should return empty list on error

@pytest.mark.asyncio
async def test_get_company_web_content_missing_api_keys(mocker):
    """
    Tests behavior when API keys are missing.
    """
    mocker.patch.dict(os.environ, clear=True) # Clear env vars for this test
    # Reload module to pick up cleared env vars
    import importlib
    importlib.reload(external_info_retriever)

    documents = await external_info_retriever.get_company_web_content("CompanyB", "services")
    assert isinstance(documents, list)
    assert len(documents) == 0