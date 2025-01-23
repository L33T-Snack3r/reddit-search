from openai import AzureOpenAI
from pydantic_settings import BaseSettings, SettingsConfigDict
from loguru import logger
import json
from typing import List
from concurrent.futures import ThreadPoolExecutor, as_completed
from redditsearch.misc.utils import find_text_in_between_tags
from redditsearch.llm.prompts import (
    system_prompt,
    post_summarize_prompt_tmpl,
    summary_summarize_prompt_tmpl
)
from redditsearch.llm.output_examples import (
    summary_examples,
    summary_summary_examples
)
import certifi
import os
#This line is necessary to get the correct SSL cert to call the openai api
os.environ["SSL_CERT_FILE"] = certifi.where()

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="azure_openai_")
    api_key : str
    endpoint : str
    version : str
    model: str = "gpt-4o"
    timeout_seconds: int = 120

cfg = Settings()

class Summarizer():
    def __init__(self,
                 openai_api_key: str = cfg.api_key,
                 openai_endpoint: str = cfg.endpoint,
                 openai_model: str = cfg.model,
                 openai_version: str = cfg.version,
                 timeout_seconds: int = cfg.timeout_seconds,
                 temperature: float = 0.0,
                 retries: int = 1
                 ):
        
        self.openai_client = AzureOpenAI(
            api_key=openai_api_key,
            azure_endpoint=openai_endpoint,
            api_version=openai_version
        )
        self.openai_model = openai_model
        self.temperature = temperature
        self.retries = retries
        self.timeout_seconds = timeout_seconds
    
        #### test
        self.testquery = "What is an apple?"
        self.testresponse = self.openai_client.chat.completions.create(
                                model=self.openai_model,
                                messages=[
                                    {"role": "user", "content": self.testquery}
                                ],
                                timeout=self.timeout_seconds,
                                temperature=self.temperature
                )
        logger.info(f"LLM call test - Query: {self.testquery} Response: {self.testresponse.choices[0].message.content}")

    def _summarize_post(self, 
                        query: str,
                        post_str: str):
        
        llm_prompt = post_summarize_prompt_tmpl.format(query=query,
                                        example_output="".join(summary_examples),
                                        reddit_post=post_str
                                        )
        
        call_tries = 0
        while call_tries <= self.retries:
            try:
                response = self.openai_client.chat.completions.create(
                                model=self.openai_model,
                                messages=[
                                    {"role": "system", "content": system_prompt},
                                    {"role": "user", "content": llm_prompt}
                                ],
                                timeout=self.timeout_seconds,
                                temperature=self.temperature
                )

                llm_output = response.choices[0].message.content
                logger.info(f"LLM output: {llm_output}")

                summary = find_text_in_between_tags(llm_output, "<<<<SUMMARY>>>>", "<<<</SUMMARY>>>>")
                keywords = find_text_in_between_tags(llm_output, "<KEYWORDS>", "</KEYWORDS>")

                keywords_list = json.loads(keywords)
                
                logger.info(f"Post ID - {find_text_in_between_tags(post_str,
                                                                    "<POST_ID>",
                                                                    "<POST_SUBREDDIT>"
                                                                    ).replace("\n", "")}: Summary generated and keywords extracted")
                return {"summary" : summary, "keywords": keywords_list}
            
            except Exception as e:
                call_tries += 1
                logger.error(f"Failed to call LLM: {e}. Retrying {call_tries}/{self.retries}")

        return {"error": "LLM call failed", "details": str(e)}

    def summarize_posts(self, query: str, 
                        post_strings: List[str], 
                        max_workers: int = 5):
        
        all_summaries, all_keywords, all_keywords_lowercase = [], set(), set()

        def add_keywords_to_set(keywords : List[str]):
            for keyword in keywords:
                if keyword.lower() not in all_keywords_lowercase:
                    all_keywords.add(keyword)
                    all_keywords_lowercase.add(keyword.lower())


        # Create a ThreadPoolExecutor with the specified number of workers
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit tasks to the executor
            future_to_post = {
                executor.submit(self._summarize_post, query, post): post
                for post in post_strings
            }

            # Collect results as they are completed
            for future in as_completed(future_to_post):
                post_str = future_to_post[future]
                try:
                    llm_output = future.result()
                    if ("summary" in llm_output) and ("keywords" in llm_output):
                        all_summaries.append(llm_output["summary"])
                        #all_keywords.update(llm_output["keywords"])
                        add_keywords_to_set(llm_output["keywords"])
                except Exception as e:
                    logger.error(f"Error processing post: {e}")

        return all_summaries, all_keywords
    
    def summarize_summaries(self, query: str,
                             summaries: List[str]
                            ):
        llm_prompt = summary_summarize_prompt_tmpl.format(
            query=query,
            example_output="".join(summary_examples),
            reddit_post_summaries="".join([f"SUMMARY {i+1}: {summary}" for i, summary in enumerate(summaries)]))
        
        call_tries = 0
        while call_tries <= self.retries:
            try:
                response = self.openai_client.chat.completions.create(
                                model=self.openai_model,
                                messages=[
                                    {"role": "system", "content": system_prompt},
                                    {"role": "user", "content": llm_prompt}
                                ],
                                timeout=self.timeout_seconds,
                                temperature=self.temperature
                )

                llm_output = response.choices[0].message.content
                overall_summary = find_text_in_between_tags(llm_output, "<SUMMARY>", "</SUMMARY>")
                logger.info(f"Overall summary: {overall_summary}")
                logger.info("Summarization of reddit summaries complete")

                return overall_summary
            
            except Exception as e:
                call_tries += 1
                logger.error(f"Failed to call LLM: {e}. Retrying {call_tries}/{self.retries}")

        raise Exception(f"LLM call failed after last retry. Error: {e}")
    
summarizer = Summarizer()