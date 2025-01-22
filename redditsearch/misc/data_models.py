from pydantic import BaseModel, ConfigDict
import pandas as pd
from typing import Dict

class Query(BaseModel):
    query: str
    maxposts: int = 5

class Response(BaseModel):
    post_data: pd.DataFrame
    comments_data: pd.DataFrame
    keyword_frequencies: Dict
    summary: str
    
    class Config:
        arbitrary_types_allowed = True
