from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
import grpc
import sys
from fastapi.staticfiles import StaticFiles


sys.path.append('../protos')

import protos.support_service_pb2 as support_service_pb2
import protos.support_service_pb2_grpc as support_service_pb2_grpc

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

def get_support_service_stub():
    channel = grpc.insecure_channel('support_service:50051')
    return support_service_pb2_grpc.SupportServiceStub(channel)

@app.get("/", response_class=HTMLResponse)
async def get(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    support_stub = get_support_service_stub()

    try:
        while True:
            data = await websocket.receive_text()
            customer_id, message = data.split("|", 1)

            # Call gRPC stream
            request = support_service_pb2.CustomerQueryRequest(
                customer_id=customer_id,
                query=message
            )
            responses = support_stub.AnswerCustomerQuery(request)

            # Stream tokens back
            for resp in responses:
                await websocket.send_text(resp.token)
                if resp.is_final:
                    await websocket.send_text("[[DONE]]")
                    break

    except WebSocketDisconnect:
        print("WebSocket disconnected")
