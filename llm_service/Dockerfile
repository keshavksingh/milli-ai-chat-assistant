FROM python:3.13.3

WORKDIR /app

COPY ./.env ./.env
COPY ./llm_service/server.py ./server.py
COPY ./llm_service/requirements.txt ./requirements.txt
COPY ./protos ./protos

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "server.py"]