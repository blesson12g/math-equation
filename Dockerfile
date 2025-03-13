FROM --platform=$TARGETPLATFORM python:3.12-slim
RUN apt update && apt install -y gcc g++ libffi-dev
RUN apt install awscli -y
RUN aws configure set default.region us-east-1
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
RUN apt install -y libglib2.0-0 libsm6 libxext6 libxrender-dev
RUN python3 -m venv /app/.venv
EXPOSE 8501
COPY . .
RUN /app/.venv/bin/python -m ensurepip && \
    /app/.venv/bin/pip install --upgrade pip setuptools wheel && \
    /app/.venv/bin/pip install -r requirements.txt && \
    /app/.venv/bin/pip install streamlit
CMD ["/app/.venv/bin/python", "-m", "streamlit", "run", "streamlit_math_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
