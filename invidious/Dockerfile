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
    ca-certificates

# Execute during the build of the image
ARG TEMPIO_VERSION BUILD_ARCH
RUN \
    curl -sSLf -o /usr/bin/tempio \
    "https://github.com/home-assistant/tempio/releases/download/${TEMPIO_VERSION}/tempio_${BUILD_ARCH}" \
    && chmod a+x /usr/bin/tempio

# Copy Invidious files from official image
COPY --from=invidious /invidious /invidious

# Copy root filesystem
COPY rootfs /

# Initialize PostgreSQL data directory and ensure service scripts are executable
RUN mkdir -p /var/lib/postgresql/data && \
    chown -R postgres:postgres /var/lib/postgresql && \
    chmod +x /etc/services.d/invidious/run /etc/services.d/invidious/finish
