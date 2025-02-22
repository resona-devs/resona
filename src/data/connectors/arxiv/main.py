import arxiv
from typing import Generator

class ArxivConnector:
    """
    A connector class for interacting with the arXiv API.
    Provides methods to search and retrieve papers from arXiv.
    """

    def __init__(self):
        """Initialize the ArxivConnector with a new client."""
        self.client = arxiv.Client()

    def search(
        self,
        query: str,
        sort_by: arxiv.SortCriterion = arxiv.SortCriterion.Relevance,
        max_results: int = 5,
    ) -> Generator[arxiv.Result, None, None]:
        """
        Perform a search using the provided parameters.

        Args:
            params: SearchParams object containing search parameters

        Returns:
            Generator of arxiv.Result objects
        """
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=sort_by,
            sort_order=arxiv.SortOrder.Descending
        )
        return self.client.results(search)
