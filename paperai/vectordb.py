from qdrant_client import QdrantClient, models
from langchain.vectorstores import Qdrant
from paperai.config import *


class DatabaseInterface():

    qdrant_client = QdrantClient(path=db_persistent_path,prefer_grpc=True)

    def __init__(self, embeddings):
        self.qdrant_db = Qdrant(
        client=self.qdrant_client, collection_name=collection_name, 
        embedding_function=embeddings.embed_query )
        self.embeddings = embeddings
        
    def reset(self) -> None:
        self.qdrant_db = None
        self.qdrant_client = None
