FROM ubuntu:19.04 as seccomp_builder
WORKDIR /tmp
ENV VERSION_RELEASE=2.4.1
ENV PYTHON3_VERSION=3.7
ENV ARCH=x86_64
RUN apt-get update
RUN apt-get install -y build-essential apt-utils software-properties-common
RUN apt-get install -y wget git
RUN apt-get install -y python3 python3-pip
RUN pip3 install cython
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
RUN buildDeps='software-properties-common git libtool cmake python-dev python3-pip python-pip'
# Add repositories
RUN add-apt-repository ppa:openjdk-r/ppa
# Update
RUN apt-get update
RUN apt-get install -y $buildDeps
# C/C++
RUN apt-get install -y gcc g++ 
# Python 2/3
RUN apt-get install -y python python3.7 python-pkg-resources python3-pkg-resources
# Java 8
RUN apt-get install -y openjdk-8-jdk

# Dependencies for Judger
RUN pip3 install --no-cache-dir pika 'dramatiq[rabbitmq]'

COPY src /judger/src
WORKDIR /judger/src
RUN apt-get install -y libseccomp-dev=${SECCOMP_VERSION}*
COPY --from=seccomp_builder /tmp/libseccomp-${SECCOMP_VERSION}/src/python/build/lib.linux-${ARCH}-${PYTHON3_VERSION}/*.so sandbox
# Clean up
# RUN apt-get purge -y --auto-remove $buildDeps
# RUN apt-get clean && rm -rf /var/lib/apt/lists/*


WORKDIR /judger/src

ARG queues="judge lint sim"

CMD [ "dramatiq", "judger_worker", "--queues", ${queues} ]
