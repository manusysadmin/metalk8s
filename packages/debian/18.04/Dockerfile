# Equal to Ubuntu:18.04
# SHA256 digest of the base image
ARG BUILD_IMAGE_SHA256=d1d454df0f579c6be4d8161d227462d69e163a8ff9d20a847533989cf0c94d90

ARG BUILD_IMAGE=docker.io/ubuntu
FROM ${BUILD_IMAGE}@sha256:${BUILD_IMAGE_SHA256} as build

ENV APT_KEY_DONT_WARN_ON_DANGEROUS_USAGE=1

RUN apt update -y \
        && \
    apt install -y \
        devscripts \
        build-essential \
        lintian \
        python-apt \
        reprepro \
        alien

RUN useradd -m build
