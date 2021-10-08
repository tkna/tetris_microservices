FROM python:alpine
WORKDIR /app
COPY ./app /app
RUN pip install Flask flask-cors
ENTRYPOINT ["python", "mino.py"] 
