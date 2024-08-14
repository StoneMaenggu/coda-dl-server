from pydantic import BaseModel, Field

class Gloss2TextRequest(BaseModel):
    gloss: str | None = Field(None, description="The gloss to be converted to text")

class Gloss2TextResponse(BaseModel):
    prediction: str | None = Field(None, description="The predicted text from the gloss")

