FROM sanicframework/sanic:3.8-latest

WORKDIR /app
COPY requirements.txt /app
RUN apk add build-base
RUN pip3 install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python3", "server.py"]
