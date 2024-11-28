FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# RUN pip install --no-cache-dir --upgrade pip \
#     && pip install --no-cache-dir -i https://pypi.org/simple \
#     ultralytics==8.0.24 \
#     Flask==1.1.2 \
#     werkzeug==1.0.1 \
#     "opencv-python>=4.6.0,<5.0.0" \
#     "opencv-python-headless>=4.6.0,<5.0.0" \
#     pandas==1.4.2 \
#     "numpy>=1.21.5,<2.0.0"


COPY . .

RUN pip install -r req.txt

EXPOSE 5000

CMD ["python", "app.py"]
