from pydantic import BaseModel, Field

class Pose2GlossRequest(BaseModel):
    pose: str | None = Field(None, description="The pose to be converted to gloss")


class Pose2GlossResponse(BaseModel):
    prediction: str | None = Field(None, description="The predicted gloss from the pose")