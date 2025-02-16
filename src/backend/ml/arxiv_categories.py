from dataclasses import dataclass
from typing import Dict, Optional
import requests
from bs4 import BeautifulSoup


@dataclass
class CategoryGroup:
    categories: Dict[str, str]

    def __getattr__(self, name):
        for cat_id, cat_name in self.categories.items():
            if cat_id.endswith(f'.{name}'):
                return cat_name
        raise AttributeError(f"No category found with suffix '{name}'")


class CategoryTaxonomy:
    def __init__(self):
        self.categories = self._fetch_categories()
        self._init_groups()

    def _fetch_categories(self) -> Dict[str, str]:
        url = 'https://arxiv.org/category_taxonomy'
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        categories = {}
        for category_div in soup.find_all('div', class_='columns divided'):
            h4_tag = category_div.find('h4')
            if h4_tag:
                category_id = h4_tag.text.strip().split(" (")[0]
                span_tag = h4_tag.find('span')
                category_name = span_tag.text.strip() if span_tag else category_id
                categories[category_id] = category_name.strip("()")

        categories.pop('Category Name\n(Category ID)', None)
        return categories

    def _init_groups(self):
        grouped = {}
        for cat_id, cat_name in self.categories.items():
            prefix = cat_id.split('.')[0] if '.' in cat_id else cat_id
            if prefix not in grouped:
                grouped[prefix] = {}
            grouped[prefix][cat_id] = cat_name

        for prefix, cats in grouped.items():
            setattr(self, prefix, CategoryGroup(cats))

    def get_category(self, category_id: str) -> Optional[str]:
        return self.categories.get(category_id)

    def list_categories(self, prefix: Optional[str] = None) -> Dict[str, str]:
        if prefix:
            return {k: v for k, v in self.categories.items() if k.startswith(f"{prefix}.")}
        return self.categories

if __name__ == "__main__":
    taxonomy = CategoryTaxonomy()
    print( f"List of all categories: {taxonomy.list_categories()}")