FROM python:3.12.7

# Set the working directory in the container
WORKDIR /app

# Install uv to install poetry
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

#Install poetry and add to path
RUN uv tool install poetry
ENV PATH="/root/.local/bin:$PATH"

#Copy app modules
COPY redditsearch /app/redditsearch
COPY app.py /app/app.py
COPY pyproject.toml poetry.lock /app/

#Install dependencies
RUN poetry install --no-root --only main

#Set env variables
ENV \
    STREAMLIT_PORT=8080 \
    STREAMLIT_HOST=0.0.0.0 \
    PYTHONPATH=/app

EXPOSE 8080

CMD ["poetry", "run", "streamlit", "run", "app.py"]