#!/bin/bash

pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
python manage.py runserver 0.0.0.0:8000