FROM ubuntu:19.04 as seccomp_builder
WORKDIR /tmp
ENV VERSION_RELEASE=2.4.1
ENV PYTHON3_VERSION=3.7
ENV ARCH=x86_64
COPY sources.list /etc/apt/sources.list
RUN apt-get update
RUN apt-get install -y apt-utils
RUN apt-get install -y --fix-missing build-essential software-properties-common
RUN apt-get install -y wget git
RUN apt-get install -y python3 python3-pip
RUN pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple cython
RUN wget -c -O libseccomp.tar.gz https://github.com/seccomp/libseccomp/releases/download/v${VERSION_RELEASE}/libseccomp-${VERSION_RELEASE}.tar.gz
RUN tar zxf libseccomp.tar.gz
WORKDIR /tmp/libseccomp-${VERSION_RELEASE}
RUN ./configure
RUN make && make install
WORKDIR /tmp/libseccomp-${VERSION_RELEASE}/src/python
RUN python3.7 setup.py build
WORKDIR /tmp/libseccomp-${VERSION_RELEASE}/src/python/build/lib.linux-${ARCH}-${PYTHON3_VERSION}
RUN ls

FROM ubuntu:19.04
ENV SECCOMP_VERSION=2.4.1
ENV PYTHON3_VERSION=3.7
ENV ARCH=x86_64
RUN buildDeps='git libtool cmake python-dev python3-pip python-pip'
# Add repositories
COPY sources.list /etc/apt/sources.list
# Update
RUN apt-get update
RUN apt-get install -y software-properties-common apt-utils
RUN apt-get install -y $buildDeps
RUN add-apt-repository ppa:openjdk-r/ppa
RUN apt-get update
# C/C++
RUN apt-get install -y gcc g++ 
# Python 2/3
RUN apt-get install -y python python3.7 python-pkg-resources python3-pkg-resources
# Java 8
RUN apt-get install -y openjdk-8-jdk

# Dependencies for Judger
RUN apt-get install -y python3-pip
RUN pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple --no-cache-dir pika 'dramatiq[rabbitmq, redis]' dacite redis amqp

RUN apt-get install -y libseccomp-dev=${SECCOMP_VERSION}*

COPY src /judger/src
WORKDIR /judger/src
COPY --from=seccomp_builder /tmp/libseccomp-${SECCOMP_VERSION}/src/python/build/lib.linux-${ARCH}-${PYTHON3_VERSION}/*.so sandbox
RUN ls -l .;ls -l sandbox
# Clean up
# RUN apt-get purge -y --auto-remove $buildDeps
# RUN apt-get clean && rm -rf /var/lib/apt/lists/*


WORKDIR /judger/src

ARG queues="judge lint sim"

# CMD [ "dramatiq", "judger_worker", "--queues", ${queues} ]
CMD [ "dramatiq", "judger_worker"]
