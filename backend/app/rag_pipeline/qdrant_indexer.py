"""This script is used to retrieve relevant documents from a given pdf and query using chromadb."""

import os
import re
import time
from typing import Any
from typing import List
from typing import Optional

from dotenv import load_dotenv

from langchain_qdrant import QdrantVectorStore
from langchain_openai import OpenAIEmbeddings
from qdrant_client import QdrantClient
from langchain.retrievers import MultiVectorRetriever



load_dotenv()


class QdrantIndexer():
    """
    A class for retrieving relevant documents from a given text using Qdrant.

    Attributes:

    Args:
        pdf_path (str): The path to the PDF file.

    Examples:

    """

    def __init__(self, documents: str):
        """
        Initializes the RetrieveRelevantDocsQdrant object.

        Args:
            pdf_path (str): The path to the PDF file.

        """
        self.documents = documents
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-large",
            # With the `text-embedding-3` class
            # of models, you can specify the size
            # of the embeddings you want returned.
            # dimensions=1024,
            )
        self.collection_name = "moog"
        self.qdrant_url = os.getenv("QDRANT_URL")
        self.qdrant_api_key = os.getenv("QDRANT_API_KEY")

        self.qdrant_client = QdrantClient(
            url=self.qdrant_url, api_key=self.qdrant_api_key
        )


    def _check_collection_exists(self):
        """
        Checks if the collection exists.

        Returns:
            bool: True if the collection exists, False otherwise.
        """
        if self.collection_name in [
            collection.name
            for collection in self.qdrant_client.get_collections().collections
        ]:
            return True
        return False

    def _create_collection(self):
        """
        Creates a collection in Qdrant.

        Returns:
            Qdrant: The Qdrant object.
        """
        print("Checking if collection exists...", self._check_collection_exists())
        # print(self.documents)
        try:
            vector_store = QdrantVectorStore.from_documents(
                self.documents,
                self.embeddings,
                url=self.qdrant_url,
                prefer_grpc=True,
                api_key=self.qdrant_api_key,
                collection_name=self.collection_name,
            )
            print("Collection created successfully.")
        except Exception as e:
            print(e)
            print("Collection creation failed.")

        return vector_store

    def get_vector_store(self):
        """
        Returns the Qdrant vector store.

        Returns:
            Qdrant: The Qdrant object.
        """
        if self._check_collection_exists():
            print("Collection exists. Making fassst...")
            print("Deleting collection...")
            self.qdrant_client.delete_collection(self.collection_name)
            # return Qdrant(
            #     client=self.qdrant_client,
            #     collection_name=self.collection_name,
            #     embeddings=self.embeddings,
            # )

        return self._create_collection()

    def get_relevant_docs(self, query: str, n_results: int = 30):
        """
        Returns a list of relevant documents.

        Args:
            query (str): The query text.
            n_results (int): The number of results to return.

        Returns:
            list: A list of relevant documents.
        """
        vector_store = self.get_vector_store()
        # results = vector_store.max_marginal_relevance_search(
        #     query, k=n_results, fetch_k=10
        # )
        retriever = vector_store.as_retriever(search_type="mmr", search_kwargs={"k": n_results})
        results = retriever.invoke(query)
        for index, doc in enumerate(results):
            print("Source number:" + str(index))
            # print(doc.page_content)
        return [[doc.page_content for doc in results]]
    
    def get_retriever(self):
        """
        Returns a retriever object.

        Returns:
            Qdrant: The Qdrant object.
        """
        vector_store = self.get_vector_store()
        retriever = MultiVectorRetriever(vector_store=vector_store)
        return retriever