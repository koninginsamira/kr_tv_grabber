FROM ubuntu:24.04
FROM node:22.11.0

# Define build arguments with default values
ARG USER=appuser
ARG GROUP=appgroup

# Set user
USER root

# Update package lists
RUN apt-get update && \
    # Install guso for lightweight user switching,
    # cron for repeating grab at set time,
    # ping for checking the internet connection,
    # and busybox for hosting the file via URL
    apt-get install -y cron gosu iputils-ping busybox && \
    # Clean up
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy files to the container
WORKDIR /
COPY ./ ./

# Make scripts executable
RUN chmod a+x /entrypoint.sh /app/cron.sh /app/grab.sh /app/host.sh /app/run.sh

# Declare volumes
VOLUME /config
VOLUME /data

# Set environment variables
ENV PUID=1000
ENV PGID=1000
ENV GUIDE_FILENAME=guide-kr
ENV BACKUP_COUNT=7
ENV RESTART_TIME=00:00
ENV HTTP=FALSE
ENV HTTP_PORT=3500

# Install Supercronic
ENV SUPERCRONIC_URL=https://github.com/aptible/supercronic/releases/download/v0.2.33/supercronic-linux-amd64 \
    SUPERCRONIC_SHA1SUM=71b0d58cc53f6bd72cf2f293e09e294b79c666d8 \
    SUPERCRONIC=supercronic-linux-amd64

RUN curl -fsSLO "$SUPERCRONIC_URL" \
    && echo "${SUPERCRONIC_SHA1SUM}  ${SUPERCRONIC}" | sha1sum -c - \
    && chmod +x "$SUPERCRONIC" \
    && mv "$SUPERCRONIC" "/usr/local/bin/${SUPERCRONIC}" \
    && ln -s "/usr/local/bin/${SUPERCRONIC}" /usr/local/bin/supercronic

# Expose port
EXPOSE 3500

# Specify the command to run your script
ENTRYPOINT ["/entrypoint.sh"]
CMD [ \
    "-u", "${USER}", "-g", "${GROUP}", \
    "-f", "/app", "-f", "/config", "-f", "/data", \
    "-r", "true", \
    "-a", "bash /app/run.sh" \
]