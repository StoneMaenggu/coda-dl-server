from pydantic import BaseModel, Field
from typing import List

class FromGloss(BaseModel):
    glosses : List[str] | None = Field(None, example=["날씨 덥다 화 난다", "목 마르다 물 마시다", "수영장 가다 놀다", "재미 있다 피곤하다 잠"], title="Gloss", description="The list of glosses of sentences")

class FromGlossResponse(BaseModel):
    image_urls: List[str] | None = Field(None, title="Filenames", description="The list of filenames of the images")
    glosses : List[str] | None = Field(None, title="Gloss", description="The list of glosses of sentences")

