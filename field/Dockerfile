FROM python:alpine
WORKDIR /app
COPY field.py /app
RUN pip install Flask flask-cors
ENTRYPOINT ["python", "field.py"] 
