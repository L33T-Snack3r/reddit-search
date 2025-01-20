import praw
import pandas as pd
from pydantic_settings import BaseSettings, SettingsConfigDict
from loguru import logger
from typing import List
from concurrent.futures import ThreadPoolExecutor, as_completed
from reddit.textprocess import(
    indent_text,
    indentation,
    post_tmpl,
    comment_tmpl,
    reply_tmpl
)

#Get Env variables
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="reddit_")
    api_id : str
    api_secret: str
    username: str
    password: str

cfg=Settings()

#Create a reply object to hold nested replies
class Reply():
    def __init__(self,
                 parent_id: str,
                 id : str,
                 content: str,
                 upvotes: int,
                 created_utc):
        
        self.parent_id =parent_id
        self.id = id
        self.content = content,
        self.upvotes = upvotes,
        self.created_utc = created_utc,
        self.replies = []

class Scraper():
    def __init__(self,
                client_id: str = cfg.api_id,
                client_secret: str = cfg.api_secret,
                username: str = cfg.username,
                password: str = cfg.password
                ):
        self.reddit = praw.Reddit(user_agent=True,
                                    client_id=client_id,
                                    client_secret=client_secret,
                                    username=username,
                                    password=password)

        logger.info("Reddit API successfully initialized.")
    
    def _get_post_ids(self, 
                       query: str,
                       max_posts: int
                       ) -> List[str]:
        search = self.reddit.subreddit('all').search(query, sort='relevance', time_filter='all', limit=max_posts)
        logger.info("Post IDs retrieved.")
        return [str(post.id) for post in search]

    def _scrape_reddit_post(self, post_id: str):
        submission = self.reddit.submission(id=post_id)
        submission.comments.replace_more(limit=0)

        #Get post data
        post_data = {
            "post_id": str(submission.id),
            "title": str(submission.title),
            "author": str(submission.author),
            "subreddit": str(submission.subreddit),
            "content": str(submission.selftext),
            "upvotes": int(submission.score),
            "downvotes": int((1.0 - submission.upvote_ratio)*submission.score),
            "created_utc":submission.created_utc
        }

        post_str = post_tmpl.format(post_subreddit=str(submission.subreddit),
                                    post_author=str(submission.author),
                                    post_title=str(submission.title),
                                    post_content=str(submission.selftext),
                                    post_upvotes=int(submission.score),
                                    post_downvotes=int((1.0 - submission.upvote_ratio)*submission.score)
                                    )

        #Get comment and replies data
        comment_data = {
            "post_id": str(submission.id),
            "comment_id": [],
            "author": [],
            "content": [],
            "upvotes": [],
            "created_utc": [],
            "replies": []
        }

        def get_replies(reply, level) -> Reply:
            nonlocal post_str
            post_str += indent_text(reply_tmpl.format(reply_content=str(reply.body)),
                                    indentation=indentation,
                                    level=level
                                    )

            rep = Reply(parent_id=reply.parent_id,
                          id=reply.id,
                          content=reply.body,
                          upvotes=reply.score,
                          created_utc=reply.created_utc)
            
            if reply.replies:
                for nested_reply in reply.replies:
                    rep.replies.append(get_replies(nested_reply, level+1))

            return rep

        for comment in submission.comments:
            comment_data["comment_id"].append(str(comment.id))
            comment_data["author"].append(str(comment.author))
            comment_data["content"].append(str(comment.body))
            comment_data["upvotes"].append(int(comment.score))
            comment_data["created_utc"].append(int(comment.created_utc))

            # appending to post txt
            post_str += indent_text(comment_tmpl.format(comment_content=str(comment.body)),
                                                        indentation=indentation,
                                                        level=1)                              

            replies = []
            for reply in comment.replies:
                replies.append(get_replies(reply, level=2))
                
            comment_data["replies"].append(replies)
        
        logger.info(f"Post ID: {post_id} - {submission.title} post & comment data of retrieved.")
        return post_data, comment_data, post_str

    def _scrape_multiple_posts(self, post_ids: List[str]):
        post_data_list, comment_data_list, post_str_list = [[] for i in range(3)]
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_post_id = {executor.submit(self._scrape_reddit_post, post_id): post_id for post_id in post_ids}
            for future in as_completed(future_to_post_id):
                post_id = future_to_post_id[future]
                try:
                    post_data, comment_data, post_str = future.result()
                    post_data_list.append(post_data)
                    comment_data_list.append(comment_data)
                    post_str_list.append(post_str)
                except Exception as exc:
                    print(f'Post ID: {post_id} generated an exception: {exc}')
        
        logger.info(f"Processing of all posts complete.")
        return post_data_list, comment_data_list, post_str_list

    def _scrape_via_post_id_search(self, query: str, max_posts: int):
        """
        1. Get post ids via reddit search
        2. Get post data in parallel via ThreadPoolExecuter
        """
        post_ids = self._get_post_ids(query=query, max_posts=max_posts)

        #Returns post_data_list, comment_data_list, post_str_list
        return self._scrape_multiple_posts(post_ids=post_ids)

    def _scrape_via_reddit_search(self, query: str, max_posts: int):
        """
        Directly scrape from the search function, runs serially
        """
        post_data_list, comment_data_list, post_str_list = [[] for i in range(3)]
        search = self.reddit.subreddit('all').search(query, sort='relevance', time_filter='all', limit=max_posts)

        for post in search:
            post.comments.replace_more(limit=0)

            #Get post data
            post_data = {
                "post_id": str(post.id),
                "title": str(post.title),
                "author": str(post.author),
                "subreddit": str(post.subreddit),
                "content": str(post.selftext),
                "upvotes": int(post.score),
                "downvotes": int((1.0 - post.upvote_ratio)*post.score),
                "created_utc":post.created_utc
            }

            post_str = post_tmpl.format(post_subreddit=str(post.subreddit),
                                        post_author=str(post.author),
                                        post_title=str(post.title),
                                        post_content=str(post.selftext),
                                        post_upvotes=int(post.score),
                                        post_downvotes=int((1.0 - post.upvote_ratio)*post.score)
                                        )

            #Get comment and replies data
            comment_data = {
                "post_id": str(post.id),
                "comment_id": [],
                "author": [],
                "content": [],
                "upvotes": [],
                "created_utc": [],
                "replies": []
            }

            def get_replies(reply, level) -> Reply:
                nonlocal post_str
                post_str += indent_text(reply_tmpl.format(reply_content=str(reply.body)),
                                        indentation=indentation,
                                        level=level
                                        )

                rep = Reply(parent_id=reply.parent_id,
                            id=reply.id,
                            content=reply.body,
                            upvotes=reply.score,
                            created_utc=reply.created_utc)
                
                if reply.replies:
                    for nested_reply in reply.replies:
                        rep.replies.append(get_replies(nested_reply, level+1))

                return rep

            for comment in post.comments:
                comment_data["comment_id"].append(str(comment.id))
                comment_data["author"].append(str(comment.author))
                comment_data["content"].append(str(comment.body))
                comment_data["upvotes"].append(int(comment.score))
                comment_data["created_utc"].append(int(comment.created_utc))

                # appending to post txt
                post_str += indent_text(comment_tmpl.format(comment_content=str(comment.body)),
                                                            indentation=indentation,
                                                            level=1)                              

                replies = []
                for reply in comment.replies:
                    replies.append(get_replies(reply, level=2))
                    
                comment_data["replies"].append(replies)

            post_data_list.append(post_data)
            comment_data_list.append(comment_data)
            post_str_list.append(post_str)
            logger.info(f"Post ID: {post.id} - {post.title} post & comment data of retrieved.")

        logger.info(f"Processing of all posts complete.")
        return post_data_list, comment_data_list, post_str_list

    def scrape_posts(self, query: str, parallel: bool = True, max_posts: int = 10):
        if parallel:
            post_data, comment_data, post_str = self._scrape_via_post_id_search(query, max_posts)
        else:
            post_data, comment_data, post_str = self._scrape_via_reddit_search(query, max_posts)
        
        explodecols = ["comment_id", "author", "content", "upvotes", "created_utc","replies"]
        return pd.DataFrame(post_data), pd.DataFrame(comment_data).explode(column=explodecols).reset_index(drop=True), post_str

scraper = Scraper()

def main():
    query = "Migraine relief"
    posts_df, comments_df, post_strs = scraper.scrape_posts(query=query,
                            parallel=True,
                            max_posts=1
                            )

    print("########POSTS DF#########")
    print(posts_df)

if __name__ == "__main__":
    main()