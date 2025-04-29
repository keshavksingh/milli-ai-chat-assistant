import grpc
from concurrent import futures
import time
from collections import defaultdict

import sys
sys.path.append('../protos')

import protos.support_service_pb2 as support_service_pb2
import protos.support_service_pb2_grpc as support_service_pb2_grpc
import protos.knowledge_service_pb2 as knowledge_service_pb2
import protos.knowledge_service_pb2_grpc as knowledge_service_pb2_grpc
import protos.llm_service_pb2 as llm_service_pb2
import protos.llm_service_pb2_grpc as llm_service_pb2_grpc

import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# gRPC client setup
def get_knowledge_service_stub():
    channel = grpc.insecure_channel('knowledge_service:50052')
    return knowledge_service_pb2_grpc.KnowledgeServiceStub(channel)

def get_llm_service_stub():
    channel = grpc.insecure_channel('llm_service:50053')
    return llm_service_pb2_grpc.LLMServiceStub(channel)

# Helper: simulate token splitting
def split_into_tokens(text):
    for token in text.split(" "):
        yield token + " "

# ---------------------
# SESSION MEMORY
# ---------------------
session_memory = defaultdict(list)  # customer_id -> list of messages

class SupportServiceServicer(support_service_pb2_grpc.SupportServiceServicer):

    def AnswerCustomerQuery(self, request, context):
        customer_id = request.customer_id
        query = request.query

        logging.info(f"Received query from customer {customer_id}: {query}")

        # Step 1: Retrieve relevant docs
        knowledge_stub = get_knowledge_service_stub()
        knowledge_request = knowledge_service_pb2.KnowledgeRequest(query=query)
        knowledge_response = knowledge_stub.RetrieveRelevantDocs(knowledge_request)

        documents = "\n".join(knowledge_response.documents)

        # Step 2: Prepare prompt
        prompt = f"Use the following documents to answer the question:\n{documents}\n\nQuestion: {query}"

        # Step 3: Retrieve memory for this session
        memory_turns = session_memory[customer_id]

        # Step 4: Call LLM with prompt + memory
        llm_stub = get_llm_service_stub()
        llm_request = llm_service_pb2.LLMRequest(
            prompt=prompt,
            memory=memory_turns
        )
        llm_response = llm_stub.GenerateAnswer(llm_request)

        full_answer = llm_response.completion

        # Step 5: Stream tokens back to user
        for token in split_into_tokens(full_answer):
            yield support_service_pb2.CustomerQueryStreamResponse(
                token=token,
                is_final=False
            )
            time.sleep(0.25)

        logging.info(f"Assistant response: for Customer Id {customer_id} : Response {full_answer}")

        # Step 6: After full response, mark as finished
        yield support_service_pb2.CustomerQueryStreamResponse(
            token="",
            is_final=True
        )

        # Step 7: Update session memory (very important)
        session_memory[customer_id].append(query)        # User's message
        session_memory[customer_id].append(full_answer)  # Assistant's reply

# Server setup
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    support_service_pb2_grpc.add_SupportServiceServicer_to_server(SupportServiceServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("SupportService gRPC server started on port 50051.")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
