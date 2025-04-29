import os
import sys
import grpc
from concurrent import futures
from dotenv import load_dotenv
import openai

sys.path.append('../protos')

import protos.llm_service_pb2 as llm_service_pb2
import protos.llm_service_pb2_grpc as llm_service_pb2_grpc

load_dotenv()

client = openai.OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

def build_messages(prompt, memory):
    """Construct the conversation history."""
    messages = [{"role": "system", "content": "You are a helpful customer support assistant."}]
    
    for i, turn in enumerate(memory):
        role = "user" if i % 2 == 0 else "assistant"
        messages.append({"role": role, "content": turn})
    
    messages.append({"role": "user", "content": prompt})
    return messages

class LLMServiceServicer(llm_service_pb2_grpc.LLMServiceServicer):
    def GenerateAnswer(self, request, context):
        prompt = request.prompt
        memory = request.memory

        messages = build_messages(prompt, memory)

        response = client.chat.completions.create(
            model="gpt-4o-mini-2024-07-18",
            messages=messages,
            temperature=0.5,
            stream=False
        )

        full_response = response.choices[0].message.content
        
        return llm_service_pb2.LLMResponse(completion=full_response)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    llm_service_pb2_grpc.add_LLMServiceServicer_to_server(LLMServiceServicer(), server)
    server.add_insecure_port('[::]:50053')
    server.start()
    print("LLMService gRPC server started on port 50053.")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
