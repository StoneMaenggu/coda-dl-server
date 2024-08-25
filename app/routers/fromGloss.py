# # from fastapi import APIRouter, HTTPException
# # from app.models.utils import p2g_module, g2t_module, t2i_module
# # from app.schemas import fromGloss as fromGloss_schema
# # from app.models.utils.s3_utils import upload_to_s3
# # import os
# # import tempfile
# # import requests
# # import uuid

# # router = APIRouter()

# # P2G = p2g_module.P2G_Module()
# # G2T = g2t_module.G2T_Module()
# # T2I = t2i_module.T2I_Module()

# # @router.post("/fromGloss", response_model= fromGloss_schema.FromGlossResponse)
# # async def fromGloss(fromGloss: fromGloss_schema.FromGloss):
# #     try:
# #         # Generate text from gloss
# #         sentences = G2T.predict(fromGloss.glosses)
# #         # Generate image from text
# #         images = T2I.predict(sentences)

# #         s3_urls = []

# #        # 임시 디렉토리에서 파일을 다운로드하고 S3에 업로드
# #         with tempfile.TemporaryDirectory() as temp_dir:
# #             for idx, image_url in enumerate(images):
# #                 try:
# #                     # 이미지 파일을 임시 디렉토리에 다운로드
# #                     response = requests.get(image_url)
# #                     file_name = f'image_{idx}_{str(uuid.uuid4())[:8]}.jpg'  # 고유한 파일 이름 생성
# #                     file_path = os.path.join(temp_dir, file_name)
# #                     with open(file_path, 'wb') as file:
# #                         file.write(response.content)
                    
# #                     # S3에 업로드하고 URL을 받아옴
# #                     s3_url = upload_to_s3(file_path, file_name)
# #                     s3_urls.append(s3_url)
# #                 except Exception as e:
# #                     raise HTTPException(status_code=500, detail=f"Error downloading image {image_url}: {str(e)}")
        
# #         return {"image_urls": s3_urls, "glosses": fromGloss.glosses}
# #     except Exception as e:
# #         raise HTTPException(status_code=400, detail=str(e))
    

# from fastapi import APIRouter, HTTPException
# from app.models.utils import p2g_module, g2t_module, t2i_module
# from app.schemas import fromGloss as fromGloss_schema
# from app.models.utils.s3_utils import upload_to_s3
# import os
# import tempfile
# import uuid
# import httpx

# router = APIRouter()

# P2G = p2g_module.P2G_Module(checkpoint_path=None, db_path=None)
# G2T = g2t_module.G2T_Module()
# T2I = t2i_module.T2I_Module()

# @router.post("/fromGloss", response_model=fromGloss_schema.FromGlossResponse)
# async def fromGloss(fromGloss: fromGloss_schema.FromGloss):
#     try:
#         # Generate text from gloss
#         sentences = G2T.predict(fromGloss.glosses)
#         # Generate image from text
#         images = T2I.predict(sentences)

#         s3_urls = []

#         # 임시 디렉토리에서 파일을 다운로드하고 S3에 업로드
#         async with httpx.AsyncClient() as client:
#             with tempfile.TemporaryDirectory() as temp_dir:
#                 for idx, image_url in enumerate(images):
#                     try:
#                         # 이미지 파일을 임시 디렉토리에 다운로드
#                         response = await client.get(image_url)
#                         response.raise_for_status()
#                         file_name = f'image_{idx}_{str(uuid.uuid4())[:8]}.jpg'  # 고유한 파일 이름 생성
#                         file_path = os.path.join(temp_dir, file_name)
#                         with open(file_path, 'wb') as file:
#                             file.write(response.content)

#                         # S3에 업로드하고 URL을 받아옴
#                         s3_url = await upload_to_s3(file_path, file_name)
#                         s3_urls.append(s3_url)
#                     except httpx.HTTPStatusError as e:
#                         raise HTTPException(status_code=502, detail=f"Error downloading image {image_url}: {str(e)}")
#                     except Exception as e:
#                         raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
        
#         return {"image_urls": s3_urls, "glosses": fromGloss.glosses}
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))

        
from fastapi import APIRouter, HTTPException
from app.models.utils import p2g_module, g2t_module, t2i_module
from app.schemas import fromGloss as fromGloss_schema
from app.models.utils.s3_utils import upload_to_s3
import os
import tempfile
import uuid
import httpx
from PIL import Image
from io import BytesIO

router = APIRouter()

P2G = p2g_module.P2G_Module(checkpoint_path=None, db_path=None)
G2T = g2t_module.G2T_Module()
T2I = t2i_module.T2I_Module()

@router.post("/fromGloss", response_model=fromGloss_schema.FromGlossResponse)
async def fromGloss(fromGloss: fromGloss_schema.FromGloss):
    try:
        # Generate text from gloss
        sentences = G2T.predict(fromGloss.glosses)
        # Generate image from text
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
        
        return {"image_urls": s3_urls, "glosses": fromGloss.glosses}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
