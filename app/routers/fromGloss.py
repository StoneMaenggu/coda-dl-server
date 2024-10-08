from fastapi import APIRouter, HTTPException
from app.modules import g2t_module, t2i_module
from app.schemas import fromGloss as fromGloss_schema
from app.modules.utils.s3_utils import upload_to_s3
import os
import tempfile
import uuid
import httpx
from PIL import Image
from io import BytesIO
import time

router = APIRouter()

G2T = g2t_module.G2T_Module()
T2I = t2i_module.T2I_Module()

# 이미지 한번에 네컷 생성
@router.post("/fromGloss", response_model=fromGloss_schema.FromGlossResponse)
async def fromGloss(fromGloss: fromGloss_schema.FromGloss):
    try:
        # Generate text from gloss
        sentences = G2T.predict(fromGloss.glosses)
        # Generate image from text
        MAX_RETRIES = 3  # 최대 재시도 횟수
        RETRY_DELAY = 2  # 재시도 간격 (초)

        try:
            image_url = retry_predict(T2I, sentences, MAX_RETRIES, RETRY_DELAY)
        except HTTPException as e:
            raise e

        s3_urls = []

        # 임시 디렉토리에서 파일을 다운로드하고 S3에 업로드
        async with httpx.AsyncClient() as client:
            with tempfile.TemporaryDirectory() as temp_dir:
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

                    # 이미지 크기와 나눌 섹션의 크기를 정의합니다.
                    img_width, img_height = image.size
                    section_width = img_width // 2
                    section_height = img_height // 2

                    # 이미지를 네 개로 나눕니다.
                    images = []
                    for i in range(2):
                        for j in range(2):
                            left = j * section_width
                            upper = i * section_height
                            right = (j + 1) * section_width
                            lower = (i + 1) * section_height

                            # 잘라낸 부분을 저장합니다.
                            cropped_image = image.crop((left, upper, right, lower))
                            images.append(cropped_image)

                    print(len(images))  # 네 개의 이미지가 있는지 확인

                    for idx, cropped_image in enumerate(images):
                        # 이미지를 JPG로 변환 및 저장
                        file_name_jpg = f'image_{idx}_{str(uuid.uuid4())[:8]}.jpg'  # 고유한 파일 이름 생성
                        file_path = os.path.join(temp_dir, file_name_jpg)
                        cropped_image.save(file_path)

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


def retry_predict(T2I, sentences, max_retries=3, retry_delay=2):
    retries = 0
    while retries < max_retries:
        try:
            # 이미지 생성 시도
            image_url = T2I.predict(sentences)
            return image_url
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                retries += 1
                print(f"404 Error: Attempt {retries}/{max_retries} failed. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                raise HTTPException(status_code=502, detail=f"Error generating image: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

    raise HTTPException(status_code=404, detail="Image generation failed after multiple attempts")