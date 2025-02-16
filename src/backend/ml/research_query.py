from pydantic import BaseModel
from datetime import date
from typing import List, Optional
from arxiv_categories import CategoryTaxonomy

# Step 4: Define the Pydantic model
class PaperFilter(BaseModel):
    primary_categories: List[CategoryTaxonomy] = [CategoryTaxonomy.cs_AI, CategoryTaxonomy.cs_RO, CategoryTaxonomy.cs_LG, CategoryTaxonomy.cs_MA]
    min_date: Optional[date] = None
    max_date: Optional[date] = None
    keywords: List[str] = ["reinforcement learning", "robot", "autonomous", "control", "multi-agent", "self-learning"]
    author_reputation: bool = True
    top_conferences: List[str] = ["NeurIPS", "ICML", "ICRA", "CVPR"]

# Example usage
filter_config = PaperFilter(min_date=date(2024, 2, 1))
print(filter_config.json(indent=4))
