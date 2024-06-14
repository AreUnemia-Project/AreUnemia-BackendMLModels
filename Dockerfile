FROM python:3.12

RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0

ENV HOST 0.0.0.0

COPY ./config /config

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

WORKDIR /app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8081"]