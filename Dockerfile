FROM node:24-slim

# Set user
USER root

WORKDIR /

# Install system packages
RUN apt-get update && apt-get install -y \
    python3 python3-venv python3-pip \
    curl cron procps \
    gosu \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Create Python virtual environment
RUN python3 -m venv /.venv
ENV PATH="/.venv/bin:$PATH"

# Install Python packages
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r ./requirements.txt

# Install Supercronic
ENV SUPERCRONIC_URL=https://github.com/aptible/supercronic/releases/download/v0.2.33/supercronic-linux-amd64 \
    SUPERCRONIC_SHA1SUM=71b0d58cc53f6bd72cf2f293e09e294b79c666d8 \
    SUPERCRONIC=supercronic-linux-amd64

RUN curl -fsSLO "$SUPERCRONIC_URL" \
    && echo "${SUPERCRONIC_SHA1SUM}  ${SUPERCRONIC}" | sha1sum -c - \
    && chmod +x "$SUPERCRONIC" \
    && mv "$SUPERCRONIC" "/usr/local/bin/${SUPERCRONIC}" \
    && ln -s "/usr/local/bin/${SUPERCRONIC}" /usr/local/bin/supercronic

COPY . .

# Make scripts executable
RUN chmod a+x /entrypoint.sh && \
    chmod a+x /app/scripts/*

# Declare volumes
VOLUME /config
VOLUME /data

# Set environment variables
ENV NODE_ENV=container
ENV PUID=1000
ENV PGID=1000
ENV GUIDE_FILENAME=guide-kr
ENV BACKUP_COUNT=7
ENV RESTART_TIME=00:00
ENV HISTORY_THRESHOLD=3
ENV FUTURE_THRESHOLD=3
ENV HTTP=FALSE
ENV HTTP_PORT=3500

# Expose port
EXPOSE 3500

# Add healthcheck for host
HEALTHCHECK --start-period=5s --interval=10s --retries=60 CMD /app/scripts/healthcheck.sh

# Specify the command to run your script
ENTRYPOINT ["/entrypoint.sh"]
CMD [ \
    "-u", "grabber", "-g", "grabber", \
    "-f", "/app", "-f", "/config", "-f", "/data", \
    "-t", "/app/scripts/title.sh", \
    "-b", "/app/scripts/before.sh", \
    "-m", "/app/scripts/run.sh", \
    "-a", "/app/scripts/after.sh" \
]