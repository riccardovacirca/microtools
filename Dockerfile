FROM ubuntu:24.04

# Metadata
LABEL maintainer="riccardovacirca"
LABEL description="Development container with s6-overlay service management"

# s6-overlay version
ENV S6_OVERLAY_VERSION=v3.2.0.0
ENV S6_VERBOSITY=1

# Install s6-overlay
RUN apt-get update && apt-get install -y \
    xz-utils \
    curl \
    ca-certificates \
    && curl -L -o /tmp/s6-overlay-noarch.tar.xz \
       https://github.com/just-containers/s6-overlay/releases/download/${S6_OVERLAY_VERSION}/s6-overlay-noarch.tar.xz \
    && tar -C / -Jxpf /tmp/s6-overlay-noarch.tar.xz \
    && curl -L -o /tmp/s6-overlay-amd64.tar.xz \
       https://github.com/just-containers/s6-overlay/releases/download/${S6_OVERLAY_VERSION}/s6-overlay-x86_64.tar.xz \
    && tar -C / -Jxpf /tmp/s6-overlay-amd64.tar.xz \
    && rm /tmp/s6-overlay-*.tar.xz \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create service directories
RUN mkdir -p /etc/services.d

# Set s6 as init system
ENTRYPOINT ["/init"]
