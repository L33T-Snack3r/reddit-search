import pandas as pd

def onehotencode(df: pd.DataFrame,
                 keywords: set,
                 content_key: str = 'content'
                 ) -> pd.DataFrame:
    
    #Drop all posts that don't have any comments
    df = df.dropna(subset = [content_key])

    for keyword in keywords:
        df[keyword] = df[content_key].str.contains(rf'\b{keyword}\b', case=False).astype(int)

    return df

def get_keyword_counts(df : pd.DataFrame,
                       keywords : set
                       ):
    
    keyword_sums = df[list(keywords)].sum()

    # Sort the keywords by their total mentions in descending order
    sorted_keywords = keyword_sums[keyword_sums > 0].sort_values(ascending=False)

    # Extract the sorted keywords and their corresponding mentions
    result = {
        "keywords": sorted_keywords.index.tolist()[:10],
        "mentions": sorted_keywords.values.tolist()[:10]
    }

    return result