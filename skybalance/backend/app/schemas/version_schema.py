from pydantic import BaseModel

class SaveVersionRequest(BaseModel):
    name: str

class VersionListResponse(BaseModel):
    versions: list