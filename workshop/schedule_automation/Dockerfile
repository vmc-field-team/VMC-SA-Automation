# Written by clennon
FROM python:3

WORKDIR /tmp/scripts

COPY requirements.txt ./
RUN python3 -m pip install --no-cache-dir --upgrade pip && \
    python3 -m pip install --no-cache-dir -r requirements.txt
