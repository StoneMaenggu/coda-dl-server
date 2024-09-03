## FastAPI를 통한 딥러닝 서버 구축
본 레포지토리에서는 실제 포스트 생성 과정에 사용되는 딥러닝 서버만을 포함하고 있으며, 기능 구현을 위한 백엔드 서버는 coda-backend 레포지토리에서 확인이 가능합니다.

## 디렉토리 구조
``` bash
├── Dockerfile
├── README.md
├── app
│   ├── main.py
│   ├── modules
│   │   ├── __init__.py
│   │   ├── g2t_module.py
│   │   ├── gap_module.py
│   │   ├── i2p_module.py
│   │   ├── p2g_module.py
│   │   ├── t2i_module.py
│   │   └── utils
│   │       ├── __init__.py
│   │       ├── access.py # access key file
│   │       ├── gloss_db
│   │       │   ├── __init__.py
│   │       │   └──  gloss_db.csv
│   │       ├── s3_utils.py
│   │       ├── timeseries_GCN.py
│   │       └── trained_model  # put .pt files
│   │           └── __init__.py
│   ├── routers
│   │   ├── __init__.py
│   │   ├── fromGloss.py
│   │   └── fromSign.py
│   └── schemas
│       ├── __init__.py
│       ├── fromGloss.py
│       └── fromSign.py
└── requirements.txt
```
