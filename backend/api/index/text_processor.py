from typing import List
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

class TextProcessor:
    @staticmethod
    def split_documents(docs: List[Document]) -> List[Document]:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            separators=["\n\n", "\n", " ", ""]
        )
        splits = []
        for doc in docs:
            doc_splits = text_splitter.split_documents([doc])
            for split in doc_splits:
                split.metadata["title"] = doc.metadata.get("title", "Unknown Title")
                split.metadata["link"] = doc.metadata.get("link", "Unknown Link")
                split.metadata["kbase"] = doc.metadata.get("kbase", "n/a")
                split.metadata["id"] = doc.metadata.get("id", "n/a")
                split.metadata["chunk_id"] = doc.metadata.get("chunk_id", "n/a")
                splits.append(split)
        return splits