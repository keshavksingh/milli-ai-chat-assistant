import os
import faiss
import pickle
import numpy as np
import grpc
from concurrent import futures
from dotenv import load_dotenv
from openai import OpenAI

import sys
sys.path.append('../protos')
load_dotenv()

import protos.knowledge_service_pb2 as knowledge_service_pb2
import protos.knowledge_service_pb2_grpc as knowledge_service_pb2_grpc

# --------------- Load FAISS Index and metadata ----------------
FAISS_INDEX_PATH = "./vectorstore/faiss_index.bin"
PRODUCT_MAPPING_PATH = "./vectorstore/product_mapping.pkl"

faiss_index = faiss.read_index(FAISS_INDEX_PATH)

with open(PRODUCT_MAPPING_PATH, "rb") as f:
    documents = pickle.load(f)

# --------------- OpenAI Client Setup ----------------
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def embed_query(text):
    response = client.embeddings.create(
        input=[text],
        model="text-embedding-3-small"
    )
    embedding = np.array(response.data[0].embedding, dtype=np.float32).reshape(1, -1)
    return embedding

# --------------- gRPC Service ----------------
class KnowledgeServiceServicer(knowledge_service_pb2_grpc.KnowledgeServiceServicer):
    def RetrieveRelevantDocs(self, request, context):
        query = request.query
        print(f"Received query: {query}")

        try:
            query_vector = embed_query(query)

            D, I = faiss_index.search(query_vector, k=5)  # Top 5 matches
            retrieved_docs = []

            for idx in I[0]:
                if idx != -1:
                    product = documents[idx]
                    doc_text = (
                        f"Product Name: {product.get('productname', '')}\n"
                        f"Description: {product.get('productdescription', '')}\n"
                        f"Price: {product.get('productprice', '')}\n"
                        f"Warranty (months): {product.get('productwarrantyinmonths', '')}"
                    )
                    retrieved_docs.append(doc_text)

            return knowledge_service_pb2.KnowledgeResponse(documents=retrieved_docs)
        
        except Exception as e:
            print(f"Error in RetrieveRelevantDocs: {e}")
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return knowledge_service_pb2.KnowledgeResponse()

# --------------- Server Startup ----------------
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    knowledge_service_pb2_grpc.add_KnowledgeServiceServicer_to_server(KnowledgeServiceServicer(), server)
    server.add_insecure_port('[::]:50052')
    server.start()
    print("KnowledgeService gRPC server started on port 50052.")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
