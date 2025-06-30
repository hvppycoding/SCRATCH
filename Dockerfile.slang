FROM centos:8

# 필수 패키지 설치
RUN dnf -y update && \
    dnf -y groupinstall "Development Tools" && \
    dnf -y install \
    git \
    cmake \
    python3 \
    python3-pip \
    gcc-c++ \
    wget \
    clang \
    llvm \
    llvm-devel \
    zlib-devel \
    ncurses-devel \
    openssl-devel \
    libffi-devel

# slang 빌드 및 설치
RUN git clone https://github.com/MikePopoloski/slang.git /opt/slang && \
    cd /opt/slang && \
    mkdir build && cd build && \
    cmake .. -DCMAKE_BUILD_TYPE=Release && \
    cmake --build . --target install

# slang 설치 확인용
RUN slang --help || echo "slang installation failed"

CMD ["/bin/bash"]
