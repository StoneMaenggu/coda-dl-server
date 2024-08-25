from fastapi import FastAPI
from app.routers import fromGloss, fromSign
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()
app.include_router(fromGloss.router)
app.include_router(fromSign.router)


# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 도메인에서의 요청 허용 (보안상 권장되지 않음)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)