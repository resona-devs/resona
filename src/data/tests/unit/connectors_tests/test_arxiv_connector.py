import pytest
from unittest.mock import Mock, patch
import arxiv
from connectors.arxiv.main import ArxivConnector

class TestArxivConnector:
    @pytest.fixture
    def mock_client(self):
        """Fixture to create a mock arxiv client"""
        with patch('arxiv.Client') as mock_client:
            yield mock_client()

    @pytest.fixture
    def connector(self, mock_client):
        """Fixture to create an ArxivConnector instance with mocked client"""
        with patch('arxiv.Client', return_value=mock_client):
            connector = ArxivConnector()
            connector.client = mock_client
            return connector

    def create_mock_result(self, title: str, authors: list[str], published: str):
        """Helper method to create mock arxiv.Result objects"""
        mock_result = Mock(spec=arxiv.Result)
        mock_result.title = title
        mock_result.authors = authors
        mock_result.published = published
        return mock_result

    def test_init_creates_client(self):
        """Test that initialization creates an arxiv client"""
        with patch('arxiv.Client') as mock_client:
            connector = ArxivConnector()
            mock_client.assert_called_once()
            assert connector.client == mock_client()

    def test_search_basic_query(self, connector, mock_client):
        """Test basic search functionality with default parameters"""
        # Prepare mock results
        mock_results = [
            self.create_mock_result(
                title="Test Paper 1",
                authors=["Author 1"],
                published="2024-01-01"
            ),
            self.create_mock_result(
                title="Test Paper 2",
                authors=["Author 2"],
                published="2024-01-02"
            )
        ]

        # Setup mock client behavior
        mock_client.results.return_value = mock_results

        # Perform search
        results = list(connector.search("machine learning"))

        # Verify search was called with correct parameters
        mock_client.results.assert_called_once()
        search_call = mock_client.results.call_args[0][0]
        assert search_call.query == "machine learning"
        assert search_call.max_results == 5
        assert search_call.sort_by == arxiv.SortCriterion.Relevance
        assert search_call.sort_order == arxiv.SortOrder.Descending

        # Verify results
        assert len(results) == 2
        assert all(isinstance(r, Mock) for r in results)
        assert results[0].title == "Test Paper 1"
        assert results[1].title == "Test Paper 2"

    def test_search_custom_parameters(self, connector, mock_client):
        """Test search with custom sort criteria and max results"""
        # Prepare mock results
        mock_results = [self.create_mock_result(
            title="Test Paper",
            authors=["Author"],
            published="2024-01-01"
        )]

        mock_client.results.return_value = mock_results

        # Perform search with custom parameters
        results = list(connector.search(
            query="physics",
            sort_by=arxiv.SortCriterion.LastUpdatedDate,
            max_results=1
        ))

        # Verify search parameters
        search_call = mock_client.results.call_args[0][0]
        assert search_call.query == "physics"
        assert search_call.max_results == 1
        assert search_call.sort_by == arxiv.SortCriterion.LastUpdatedDate
        assert len(results) == 1

    def test_search_empty_results(self, connector, mock_client):
        """Test search when no results are found"""
        # Setup mock to return empty results
        mock_client.results.return_value = []

        # Perform search
        results = list(connector.search("nonexistent_topic_12345"))

        # Verify behavior with empty results
        assert len(results) == 0
        mock_client.results.assert_called_once()

    def test_search_with_error(self, connector, mock_client):
        """Test search behavior when an error occurs"""
        # Setup mock to raise an exception
        mock_client.results.side_effect = Exception("API Error")

        # Verify that the exception is propagated
        with pytest.raises(Exception) as exc_info:
            list(connector.search("query"))

        assert str(exc_info.value) == "API Error"
        mock_client.results.assert_called_once()

    @pytest.mark.parametrize("max_results", [-1, 0, 101])
    def test_search_invalid_max_results(self, connector, mock_client, max_results):
        """Test search with invalid max_results values"""
        # Perform search with invalid max_results
        # Note: If the arxiv library doesn't validate these,
        # you might want to add validation in your connector
        results = list(connector.search("query", max_results=max_results))
        # Verify that the search was attempted
        mock_client.results.assert_called_once()
        search_call = mock_client.results.call_args[0][0]
        assert search_call.max_results == max_results
