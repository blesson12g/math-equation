# Use multi-platform build
FROM --platform=$TARGETPLATFORM python:3.12-slim

# Install necessary dependencies
RUN apt update && apt install -y gcc g++ libffi-dev unzip curl

# Determine architecture and install the correct AWS CLI version
RUN ARCH=$(dpkg --print-architecture) && \
    if [ "$ARCH" = "arm64" ]; then \
        CLI_URL="https://awscli.amazonaws.com/awscli-exe-linux-aarch64.zip"; \
    else \
        CLI_URL="https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip"; \
    fi && \
    curl "$CLI_URL" -o "awscliv2.zip" && \
    unzip awscliv2.zip && \
    ./aws/install --bin-dir /usr/local/bin --install-dir /usr/local/aws-cli --update && \
    aws --version

# Configure AWS CLI
RUN aws configure set default.region us-east-1

# Install additional dependencies
RUN apt-get update && apt-get install -y ffmpeg libsm6 libxext6 libglib2.0-0 libxrender-dev

# Set up virtual environment
RUN python3 -m venv /app/.venv

# Expose Streamlit port
EXPOSE 8501

# Copy application files
COPY . .

# Install Python dependencies inside the virtual environment
RUN /app/.venv/bin/python -m ensurepip && \
    /app/.venv/bin/pip install --upgrade pip setuptools wheel && \
    /app/.venv/bin/pip install -r requirements.txt && \
    /app/.venv/bin/pip install streamlit

# Start the Streamlit app
CMD ["/app/.venv/bin/python", "-m", "streamlit", "run", "streamlit_math_app.py", "--server.port=8501", "--server.address=0.0.0.0"]

