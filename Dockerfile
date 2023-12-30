# Dockerfile
FROM python:3.11-slim

COPY . /app

# Set the working directory to /app
WORKDIR /app

RUN pip install -r requirements.txt

ENV FLASK_APP="app.py"
ENV FLASK_DEBUG=1

EXPOSE 5000

CMD ["sh", "-c", "sleep 5 \ 
    && python -m flask run --host=0.0.0.0"]
