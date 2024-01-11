FROM python:3.8.5
WORKDIR /data
COPY ./ /data

RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
EXPOSE 8999
CMD echo "-----successful------"
CMD /bin/bash start.sh