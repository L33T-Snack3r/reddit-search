from redditsearch.reddit.scrape import scraper
from redditsearch.llm.summarize import summarizer
from redditsearch.llm.postprocessing import (
    onehotencode,
    get_keyword_counts
)
from redditsearch.data_models import (
    Query,
    Response
)

def search(query : Query) -> Response:

    posts_df, comments_df, post_strs = scraper.scrape_posts(query.query, 
                                                            parallel=True, 
                                                            max_posts=query.maxposts)
    
    summaries, all_keywords = summarizer.summarize_posts(query=query,
                                                         post_strings=post_strs)
    
    overall_summary = summarizer.summarize_summaries(query=query,
                                                     summaries=summaries)
    comments_df = onehotencode(df=comments_df,
                               keywords=all_keywords,
                               content_key='content')
    
    comments_keyword_frequencies = get_keyword_counts(df=comments_df,
                                                      keywords=all_keywords)
    
    return Response(post_data=posts_df,
                    comments_data=comments_df,
                    summary=overall_summary,
                    keyword_frequencies=comments_keyword_frequencies
                    )
