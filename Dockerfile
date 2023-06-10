FROM nvidia/cuda:11.8.0-devel-ubuntu22.04

ARG PYTHON_VERSION=3.10

ENV PYTHONUNBUFFERED 1
ENV OPENCV_LOG_LEVEL ERROR
ENV OPENCV_VIDEOIO_DEBUG 0
ENV DEBIAN_FRONTEND noninteractive
ENV TZ "Asia/Tokyo"
ENV NVIDIA_VISIBLE_DEVICES all
ENV NVIDIA_DRIVER_CAPABILITIES compute,video,utility

WORKDIR /workspaces/

RUN apt-get update -y && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    cuda-nvcc-11-8 \
    curl \
    ffmpeg \
    git \
    # libcublas-dev-11-8 \
    libcudnn8-dev \
    nvidia-gds-11-8 \
    software-properties-common \
    sysstat \
    tree \
    tmux \
    tzdata \
    unp \
    unrar-free \
    wget \
    xkb-data \
    && apt-get clean

# install rust
# RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
RUN curl https://sh.rustup.rs -sSf | bash -s -- -y

# install python
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt install python${PYTHON_VERSION}-dev python${PYTHON_VERSION}-venv python3-pip -y
RUN ln -s /usr/bin/python${PYTHON_VERSION} /usr/bin/python

RUN python -m pip install -U pip
RUN python -m pip install -U nvidia-pyindex

ADD requirements.txt .
RUN python -m pip install -r requirements.txt \
    --upgrade-strategy only-if-needed \
    --ignore-installed
