from pydantic import BaseModel
from fastapi import Form, UploadFile, File

class IndexRequest(BaseModel):
    kbase_name: str

    @classmethod
    def as_form(cls, kbase_id: str = Form(...), file: UploadFile = File(...)):
        return cls(kbase_id=kbase_id)


class IndexResponse(BaseModel):
    message: str
    s3_uri: str