FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

# remove all default files in the workdir
RUN rm -rf /app

COPY . /app
RUN python -m pip install --no-cache-dir -r requirements.txt

ENV PYTHONPATH=/app/app