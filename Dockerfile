FROM sanicframework/sanic:3.8-latest

WORKDIR /app
COPY . .
RUN apk add build-base
RUN pip3 install -r requirements.txt
# RUN python3 populate_w_textdata.py
EXPOSE 8000
CMD ["python3", "server.py"]
