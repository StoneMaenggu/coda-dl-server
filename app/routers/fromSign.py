from fastapi import APIRouter, HTTPException, File, UploadFile
from app.models.utils import i2p_module, p2g_module, g2t_module, t2i_module
from app.schemas import fromSign as fromSign_schema
from app.models.utils.s3_utils import upload_to_s3
import os
import tempfile
import requests
import uuid
from typing import List
import numpy as np
import httpx
from PIL import Image
from io import BytesIO

router = APIRouter()

I2P = i2p_module.I2P_Module()
P2G = p2g_module.P2G_Module(checkpoint_path=None,db_path=None)
G2T = g2t_module.G2T_Module()
T2I = t2i_module.T2I_Module()

@router.post("/fromSign", response_model= fromSign_schema.FromSignResponse)
async def fromSign(files: List[UploadFile] = File(...)):
    try:
        seq1 = files[:100]
        seq2 = files[100:200]
        seq3 = files[200:300]
        seq4 = files[300:400]
        
        total_seq_gloss = []
        for seq in [seq1, seq2, seq3, seq4]:
            tmp_seq_pose = []
            for file in seq:
                if file.content_type != "image/jpeg":
                    raise HTTPException(status_code=400, detail="Only JPEG images are allowed.")
                tmp_file = await file.read()
                tmp_pose = I2P.predict(tmp_file)
                tmp_seq_pose.append(tmp_pose)
            tmp_seq_pose = np.array(tmp_seq_pose) # 이거 normalize P2G에 추가해준다고함.
            tmp_seq_feat = P2G.predict(tmp_seq_pose)
            tmp_seq_gloss = "날씨 덥다 화 난다"
            total_seq_gloss.append(tmp_seq_gloss)
        
        sentences = G2T.predict(total_seq_gloss)
        images = T2I.predict(sentences)

        s3_urls = []

        # 임시 디렉토리에서 파일을 다운로드하고 S3에 업로드
        async with httpx.AsyncClient() as client:
            with tempfile.TemporaryDirectory() as temp_dir:
                for idx, image_url in enumerate(images):
                    try:
                        # 이미지 파일을 임시 디렉토리에 다운로드
                        print(image_url)
                        response = await client.get(image_url)
                        response.raise_for_status()
                        
                        content_type = response.headers.get('Content-Type')
                        print(content_type)
                        if 'image' not in content_type:
                            raise HTTPException(status_code=400, detail=f"URL does not point to an image: {image_url}")
                        # 이미지를 PIL Image 객체로 변환
                        image = Image.open(BytesIO(response.content))
            
                        print(image.mode)
                        
                        # 이미지를 JPG로 변환 및 저장
                        # file_name_png = f'image_{idx}_{str(uuid.uuid4())[:8]}.png'  # 고유한 파일 이름 생성
                        file_name_jpg = f'image_{idx}_{str(uuid.uuid4())[:8]}.jpg'  # 고유한 파일 이름 생성
                        file_path = os.path.join(temp_dir, file_name_jpg)
                        image.save(file_path)

                        # S3에 업로드하고 URL을 받아옴
                        s3_url = await upload_to_s3(file_path, file_name_jpg)
                        s3_urls.append(s3_url)
                    except httpx.HTTPStatusError as e:
                        raise HTTPException(status_code=502, detail=f"Error downloading image {image_url}: {str(e)}")
                    except Exception as e:
                        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
        
        return {"image_urls": s3_urls, "glosses": total_seq_gloss}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))



# @router.post("/fromSign", response_model= fromSign_schema.FromSignResponse)
# async def fromSign(files: List[UploadFile] = File(...)):
#     try:
#         seq1 = files[:100]
#         seq2 = files[100:200]
#         seq3 = files[200:300]
#         seq4 = files[300:400]
        
#         total_seq_gloss = []
#         for seq in [seq1, seq2, seq3, seq4]:
#             tmp_seq_pose = []
#             for file in seq:
#                 if file.content_type != "image/jpeg":
#                     raise HTTPException(status_code=400, detail="Only JPEG images are allowed.")
#                 tmp_file = await file.read()
#                 tmp_pose = I2P.predict(tmp_file)
#                 tmp_seq_pose.append(tmp_pose)
#             tmp_seq_pose = np.array(tmp_seq_pose) # 이거 normalize P2G에 추가해준다고함.
#             tmp_seq_feat = P2G.predict(tmp_seq_pose)
#             tmp_seq_gloss = "날씨 덥다 화 난다"
#             total_seq_gloss.append(tmp_seq_gloss)
        
#         sentences = G2T.predict(total_seq_gloss)
#         images = T2I.predict(sentences)

#         s3_urls = []

#        # 임시 디렉토리에서 파일을 다운로드하고 S3에 업로드
#         with tempfile.TemporaryDirectory() as temp_dir:
#             for idx, image_url in enumerate(images):
#                 try:
#                     # 이미지 파일을 임시 디렉토리에 다운로드
#                     response = requests.get(image_url)
#                     file_name = f'image_{idx}_{str(uuid.uuid4())[:8]}.jpg'  # 고유한 파일 이름 생성
#                     file_path = os.path.join(temp_dir, file_name)
#                     with open(file_path, 'wb') as file:
#                         file.write(response.content)
                    
#                     # S3에 업로드하고 URL을 받아옴
#                     s3_url = await upload_to_s3(file_path, file_name)
#                     s3_urls.append(s3_url)
#                 except Exception as e:
#                     raise HTTPException(status_code=500, detail=f"Error downloading image {image_url}: {str(e)}")
        
#         return {"image_urls": s3_urls, "glosses": total_seq_gloss}
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))
