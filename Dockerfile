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
    # and ping for checking the internet connection
    apt-get install -y gosu iputils-ping && \
    # Clean up
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy files to the container
WORKDIR /
COPY ./ ./

# Make scripts executable
RUN chmod a+x /entrypoint.sh /app/app.sh

# Declare volumes
VOLUME /config
VOLUME /data

# Set environment variables
ENV PUID=1000
ENV PGID=1000
ENV GUIDE_FILENAME=guide-kr
ENV BACKUP_COUNT=7
ENV RESTART_TIME=00:00

# Specify the command to run your script
ENTRYPOINT ["/entrypoint.sh"]
CMD [ \
    "-u", "${USER}", "-g", "${GROUP}", \
    "-f", "/app", "-f", "/config", "-f", "/data", \
    "-a", "bash /app/app.sh" \
]