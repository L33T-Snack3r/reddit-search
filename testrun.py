from redditsearch.engine import search
from redditsearch.misc.data_models import Query
import certifi
import os
from loguru import logger

logger.info(f"SSL cert: {certifi.where()}")
os.environ["SSL_CERT_FILE"] = certifi.where()

query = "chronic backache relief"
payload = Query(query=query, maxposts=7)
response = search(payload)

print(response.summary)