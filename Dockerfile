FROM ubuntu:24.04
FROM node:22.11.0

WORKDIR /

# Copy files
COPY ./ ./

# Prepare entrypoint
RUN chmod a+x run.sh

VOLUME /data

ENV GUIDE_FILE=guide-kr
ENV BACKUP_COUNT=7
ENV RESTART_TIME=00:00

ENTRYPOINT ["bash", "./run.sh"]