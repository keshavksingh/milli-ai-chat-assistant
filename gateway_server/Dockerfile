FROM python:3.13.3

WORKDIR /app

COPY ./gateway_server/main.py ./main.py
COPY ./gateway_server/requirements.txt ./requirements.txt
COPY ./gateway_server/templates ./templates
COPY ./gateway_server/static ./static
COPY ./protos ./protos

RUN pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
#python -m grpc_tools.protoc -I=protos --python_out=protos --grpc_python_out=protos protos/support_service.proto protos/knowledge_service.proto protos/llm_service.proto