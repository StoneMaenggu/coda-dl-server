## Directory
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
