# reddit-search

### Motivation: Aggregate search of medical-related reddit posts
This idea of this app is to serve as a quick aggregate search engine of reddit posts related to medical advice (It hasn't been optimized for regular search yet).

Often when seeking advice before making a decision or searching for solutions to a problem, a good first point of reference is reddit.

### Getting started
1. Create a virtual environment and install dependencies via pyproject.toml or requirements.txt.
2. Make a copy of .env-sample and save as .env, then fill in the necessary information for the APIs below
    - Azure OpenAI API
    - PRAW reddit API
3. Activate your virtual environment and run `streamlit run app.py` or `python testrun.py`from within the project root folder
