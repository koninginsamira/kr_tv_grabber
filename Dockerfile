# ===========================================
# Python setup
# ===========================================
FROM python:3 AS python

# Set user
USER root

WORKDIR /

# Create Python environment
RUN python -m venv /.venv
ENV PATH="/.venv/bin:$PATH"

# Install Python packages
COPY requirements.txt .
RUN pip install -r ./requirements.txt

# ===========================================
# NodeJS setup
# ===========================================
FROM node:23

# Install Linux packages
RUN apt-get update && \
    # Install cron for repeating grab at set time,
    # guso for lightweight user switching,
    # and python3 for the app itself
    apt-get install -y cron gosu python3

# Install Supercronic
ENV SUPERCRONIC_URL=https://github.com/aptible/supercronic/releases/download/v0.2.33/supercronic-linux-amd64 \
    SUPERCRONIC_SHA1SUM=71b0d58cc53f6bd72cf2f293e09e294b79c666d8 \
    SUPERCRONIC=supercronic-linux-amd64

RUN curl -fsSLO "$SUPERCRONIC_URL" \
    && echo "${SUPERCRONIC_SHA1SUM}  ${SUPERCRONIC}" | sha1sum -c - \
    && chmod +x "$SUPERCRONIC" \
    && mv "$SUPERCRONIC" "/usr/local/bin/${SUPERCRONIC}" \
    && ln -s "/usr/local/bin/${SUPERCRONIC}" /usr/local/bin/supercronic

WORKDIR /

# Get Python environment
COPY --from=python /.venv /.venv
ENV PATH="/.venv/bin:$PATH"
ENV NODE_ENV=container

# # Install Node packages
# COPY package*.json .
# RUN npm install

# ===========================================
# App setup
# ===========================================
COPY . .

# Make scripts executable
RUN chmod a+x /entrypoint.sh
RUN chmod a+x /app/scripts/*

# Declare volumes
VOLUME /config
VOLUME /data

# Set environment variables
ENV PUID=1000
ENV PGID=1000
ENV GUIDE_FILENAME=guide-kr
ENV BACKUP_COUNT=7
ENV RESTART_TIME=00:00
ENV HISTORY_THRESHOLD=3
ENV FUTURE_THRESHOLD=3
ENV HTTP=FALSE
ENV HTTP_PORT=3500

# Clean up
RUN rm -rf ./requirements.txt package*.json
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# Expose port
EXPOSE 3500

# Add healthcheck for host
HEALTHCHECK --interval=10s --timeout=10s --start-period=5s CMD /app/scripts/healthcheck.sh

# Specify the command to run your script
ENTRYPOINT ["/entrypoint.sh"]
CMD [ \
    "-u", "grabber", "-g", "grabber", \
    "-f", "/app", "-f", "/config", "-f", "/data", \
    "-b", "bash /app/scripts/before.sh", \
    "-a", "bash /app/scripts/run.sh" \
]