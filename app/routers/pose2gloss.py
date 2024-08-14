from fastapi import APIRouter
import app.schemas.pose2gloss as pose2gloss_schema
from app.models.pose2gloss import predict_pose2gloss

router = APIRouter()

@router.post("/pose2gloss", response_model=pose2gloss_schema.Pose2GlossResponse)
async def pose2gloss(pose2gloss_request: pose2gloss_schema.Pose2GlossRequest):
    prediction = predict_pose2gloss(pose2gloss_request.pose)
    return pose2gloss_schema.Pose2GlossResponse(prediction=prediction)