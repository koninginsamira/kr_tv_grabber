FROM ubuntu:24.04
FROM node:22.11.0

WORKDIR /

# Install tini for proper signal handling
RUN apt-get update && apt-get install -y tini && apt-get clean

# Copy files to the container
COPY ./ ./

# Make the script executable
RUN chmod a+x run.sh

# Declare volumes
VOLUME /config
VOLUME /data

# Set environment variables
ENV GUIDE_FILENAME=guide-kr
ENV BACKUP_COUNT=7
ENV RESTART_TIME=00:00

# Use tini as the entrypoint to handle signals
ENTRYPOINT ["/usr/bin/tini", "--"]

# Specify the command to run your script
CMD ["bash", "./run.sh"]