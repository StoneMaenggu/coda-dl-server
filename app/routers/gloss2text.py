from fastapi import APIRouter
import app.schemas.gloss2text as gloss2text_schema
from app.models.gloss2text import predict_gloss2text

router = APIRouter()

@router.post("/gloss2text", response_model=gloss2text_schema.Gloss2TextResponse)
async def gloss2text(gloss2text_request: gloss2text_schema.Gloss2TextRequest):
    prediction = predict_gloss2text(gloss2text_request.gloss)
    return gloss2text_schema.Gloss2TextResponse(prediction=prediction)