FROM python:alpine
WORKDIR /app
COPY ./app /app
RUN pip install Flask flask-cors requests
ENTRYPOINT ["python", "mino.py"] 
