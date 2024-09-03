import os
import uuid
import tempfile
import shutil
from typing import List
from fastapi import APIRouter, File, UploadFile, HTTPException
from moviepy.editor import VideoFileClip
from PIL import Image
import numpy as np
import cv2
import httpx
import ast
from io import BytesIO
from app.modules import i2p_module, p2g_module, g2t_module, t2i_module, gap_module
from app.schemas import fromSign as fromSign_schema
from app.modules.utils.s3_utils import upload_to_s3

router = APIRouter()

I2P = i2p_module.I2P_Module()
P2G = p2g_module.P2G_Module(checkpoint_path='app/models/utils/trained_model/epoch_last_gcn_mom.pt',db_path="app/models/utils/gloss_db/gloss_db_mom.csv")
GAP = gap_module.GAP_Module()
G2T = g2t_module.G2T_Module()
T2I = t2i_module.T2I_Module()

@router.post("/fromSign", response_model=fromSign_schema.FromSignResponse)
async def fromSign(files: List[UploadFile] = File(...)):
    temp_dir = tempfile.mkdtemp()
    image_files = []
    
    try:
        # video -> image
        frame_rate = 30
        
        for idx, file in enumerate(files):
            if file.content_type not in ["video/mp4", "video/quicktime"]:
                raise HTTPException(status_code=400, detail="Only MP4 and MOV video files are allowed.")
            
            # 비디오 파일을 임시 파일로 저장
            temp_video_path = os.path.join(temp_dir, f"temp_video_{idx}.{file.filename.split('.')[-1]}")
            with open(temp_video_path, "wb") as temp_video_file:
                temp_video_file.write(await file.read())
            
            print('video file saved as tmp')

            # moviepy를 사용하여 비디오에서 프레임 추출
            video_clip = VideoFileClip(temp_video_path)
            duration = video_clip.duration
            num_frames = int(duration * frame_rate)

            print('video frame check')
            tmp_image_list = []
            for i in range(num_frames):
                # 프레임 추출 및 저장
                frame_time = i / frame_rate
                frame = video_clip.get_frame(frame_time)
                img = Image.fromarray(frame)
                
                file_name_jpg = f"frame_{idx}_{i}_{str(uuid.uuid4())[:8]}.jpg"
                file_path = os.path.join(temp_dir, file_name_jpg)
                img.save(file_path)
                
                # 이미지 파일 리스트에 추가
                tmp_image_list.append(file_path)
            image_files.append(tmp_image_list)
            print('frame extracted')

        # image sequence
        print('seq len', len(image_files))
    
        total_seq_gloss = []
        
        print('start seq loop')
        for seq in image_files:
            tmp_seq_pose = []
            for file_path in seq:
                with open(file_path, "rb") as img_file:
                    tmp_file = img_file.read()

                # 이미지 로드 및 변환
                np_img = np.frombuffer(tmp_file, np.uint8)
                image = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
                if image is None:
                    raise HTTPException(status_code=400, detail="Could not decode image file.")
                
                # BGR to RGB 변환
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                
                tmp_pose = I2P.predict(image_rgb) # pose estimation
                tmp_seq_pose.append(tmp_pose)
            
            tmp_seq_pose = np.array(tmp_seq_pose)
            tmp_seq_gloss = P2G.predict(tmp_seq_pose) # pose to gloss
            total_seq_gloss.append(tmp_seq_gloss)
        
        print('P2G done')

        # gloss after-processing
        total_seq_gloss = GAP.predict(total_seq_gloss)
        print('GAP done')

        # 문자열을 리스트로 변환
        total_seq_gloss = ast.literal_eval(total_seq_gloss)
        print('list of gaped sentences:', total_seq_gloss)

        sentences = G2T.predict(total_seq_gloss) # gloss to text
        print(sentences)
        print('G2T done')
        image_url = T2I.predict(sentences) # text to image
        print('T2I done')

        s3_urls = []

        # 임시 디렉토리에서 파일을 다운로드하고 S3에 업로드
        async with httpx.AsyncClient() as client:
            with tempfile.TemporaryDirectory() as inner_temp_dir:
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
                        file_path = os.path.join(inner_temp_dir, file_name_jpg)
                        cropped_image.save(file_path)

                        # S3에 업로드하고 URL을 받아옴
                        s3_url = await upload_to_s3(file_path, file_name_jpg)
                        s3_urls.append(s3_url)
                except httpx.HTTPStatusError as e:
                    raise HTTPException(status_code=502, detail=f"Error downloading image {image_url}: {str(e)}")
                except Exception as e:
                    raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
        
        print('s3 upload done')

        if len(image_files) == 1:
            total_seq_gloss = total_seq_gloss * 4
        elif len(image_files) == 2:
            total_seq_gloss = total_seq_gloss * 2
        elif len(image_files) == 3:
            total_seq_gloss = total_seq_gloss + total_seq_gloss[0]
        else:
            total_seq_gloss = total_seq_gloss

        print('image_urls:', s3_urls, 'glosses:', total_seq_gloss)
        return {"image_urls": s3_urls, "glosses": total_seq_gloss}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        # 임시 디렉토리 삭제
        try:
            shutil.rmtree(temp_dir)
        except Exception as cleanup_error:
            print(f"Error during cleanup: {cleanup_error}")

