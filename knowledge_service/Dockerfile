FROM python:3.13.3

WORKDIR /app

COPY ./.env ./.env
COPY ./knowledge_service/server.py ./server.py
COPY ./knowledge_service/requirements.txt ./requirements.txt
COPY ./protos ./protos
COPY ./vectorstore ./vectorstore

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "server.py"]