# https://developers.home-assistant.io/docs/add-ons/configuration#add-on-dockerfile
ARG BUILD_FROM
FROM quay.io/invidious/invidious:latest AS invidious

FROM $BUILD_FROM

# Install PostgreSQL and dependencies
RUN apk add --no-cache \
    postgresql \
    postgresql-contrib \
    pwgen \
    curl \
    ca-certificates \
    python3 \
    py3-pip \
    py3-aiohttp \
    py3-websockets

# Execute during the build of the image
ARG TEMPIO_VERSION BUILD_ARCH
RUN \
    curl -sSLf -o /usr/bin/tempio \
    "https://github.com/home-assistant/tempio/releases/download/${TEMPIO_VERSION}/tempio_${BUILD_ARCH}" \
    && chmod a+x /usr/bin/tempio

# Install MCP server and Home Assistant client
RUN pip3 install --no-cache-dir --break-system-packages \
    mcp \
    homeassistant-api

# Copy Invidious files from official image
COPY --from=invidious /invidious /invidious

# Copy root filesystem
COPY rootfs /

# Initialize PostgreSQL data directory and ensure service scripts are executable
RUN mkdir -p /var/lib/postgresql/data && \
    chown -R postgres:postgres /var/lib/postgresql && \
    chmod +x /etc/services.d/invidious/run /etc/services.d/invidious/finish && \
    chmod +x /etc/services.d/mcp-server/run /etc/services.d/mcp-server/finish /usr/local/bin/mcp-server.py
