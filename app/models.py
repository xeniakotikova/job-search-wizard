from pydantic import BaseModel


class JobResult(BaseModel):
    title: str
    description: str
    link: str
    date: str | None = None
