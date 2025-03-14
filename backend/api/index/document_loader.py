import os
import boto3
import uuid
from langchain_community.document_loaders.pdf import AmazonTextractPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from urllib.parse import urlparse

class DocumentLoader:
    def __init__(self, kbase_name: str):
        self.bucket = os.getenv("AWS_BUCKET")
        self.region = os.getenv("AWS_REGION")
        self.access_key = os.getenv("AWS_ACCESS_KEY_ID")
        self.secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        self.kbase_name = kbase_name
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name=self.region,
        )
        self.textract_client = boto3.client(
            "textract",
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name=self.region,
        )

    def load_documents(self, uris: list) -> list:
        documents = []
        for uri in uris:
            if uri.startswith("s3://"):
                documents.extend(self._load_s3_document(uri))
            else:
                print(f"Unsupported URI: {uri}")
        return documents

    def _load_s3_document(self, uri: str) -> list:
        bucket, key = self._parse_s3_uri(uri)
        file_name = key.split("/")[-1]
        file_size = self._check_s3_file_size(uri)

        docs = []
        document_uuid = str(uuid.uuid4())

        if file_size > 10_000_000:  # 10MB
            split_filenames = self._split_pdf(uri)
            for i, split_filename in enumerate(split_filenames):
                print(f"Processing split file: {split_filename}")
                loader = AmazonTextractPDFLoader(file_path=split_filename, client=self.textract_client)
                split_docs = loader.load_and_split(
                    text_splitter=RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
                )
                for j, doc in enumerate(split_docs):
                    doc.metadata["chunk_id"] = f"{i}_{j}"
                    doc.metadata["id"] = document_uuid
                    docs.append(doc)
        else:
            print(f"Processing file directly: {uri}")
            loader = AmazonTextractPDFLoader(file_path=uri, client=self.textract_client)
            split_docs = loader.load_and_split()
            for i, doc in enumerate(split_docs):
                doc.metadata["chunk_id"] = str(i)
                doc.metadata["id"] = document_uuid
                docs.append(doc)

        for doc in docs:
            doc.metadata["title"] = file_name
            doc.metadata["link"] = uri
            doc.metadata["kbase"] = self.kbase_name

        return docs

    def _parse_s3_uri(self, uri: str):
        parsed = urlparse(uri)
        return parsed.netloc, parsed.path.lstrip("/")

    def _check_s3_file_size(self, s3_uri: str):
        bucket, key = self._parse_s3_uri(s3_uri)
        response = self.s3_client.head_object(Bucket=bucket, Key=key)
        return response["ContentLength"]

    def _split_pdf(self, s3_uri: str):
        # Placeholder for actual PDF splitting logic.
        return [s3_uri]