FROM python:3.11-slim

ENV LANG=C.UTF-8

# Install system dependencies
RUN apt-get update -y && apt-get install -y --no-install-recommends --fix-missing \
    build-essential \
    libjemalloc-dev \
    libgl1-mesa-glx

# Install Python packages globally


# Create user
RUN useradd -m -s /bin/bash user && \
    mkdir -p /home/user/comps/feedback_management/arango && \
    chown -R user /home/user

USER user

COPY comps /home/user/comps
COPY requirements.txt /home/user/

RUN pip install --no-cache-dir --upgrade pip setuptools && \
    pip install --no-cache-dir -r /home/user/comps/feedback_management/arango/requirements.txt && \
    pip install --no-cache-dir -r /home/user/requirements.txt   

ENV PYTHONPATH=/home/user/

WORKDIR /home/user/comps/feedback_management/arango
RUN pip install -r requirements.txt

ENTRYPOINT ["python", "feedback.py"]
