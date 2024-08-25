from pydantic import BaseModel, Field
from typing import List

class FromSignResponse(BaseModel):
    image_urls: List[str] | None = Field(None, title="Filenames", description="The list of filenames of the images")
    glosses : List[str] | None = Field(None, title="Gloss", description="The list of glosses of sentences")
