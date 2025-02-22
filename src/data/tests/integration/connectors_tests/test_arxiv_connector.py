import pytest
import arxiv
from connectors.arxiv.main import ArxivConnector

def test_arxiv_search():
    """
    Integration test for the ArxivConnector search method.
    Ensures that a valid response is returned.
    """
    connector = ArxivConnector()
    results = connector.search("machine learning", max_results=3)

    results_list = list(results)  # Convert generator to list for assertions
    assert len(results_list) > 0, "No results returned from arXiv API"

    for result in results_list:
        assert isinstance(result, arxiv.Result), "Result is not an instance of arxiv.Result"
        assert hasattr(result, "title"), "Result does not have a title"
        assert hasattr(result, "authors"), "Result does not have authors"
        assert hasattr(result, "summary"), "Result does not have a summary"
        assert hasattr(result, "pdf_url"), "Result does not have a PDF URL"

if __name__ == "__main__":
    pytest.main()
