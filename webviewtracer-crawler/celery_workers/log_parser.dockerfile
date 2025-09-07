# TODO: add frida log parser
ARG DOCKER_IMAGE=visiblev8/vv8-base:latest

FROM visiblev8/vv8-base:latest as vv8

FROM $DOCKER_IMAGE AS postprocessor

FROM python:3.10-slim

# Create vv8 user
RUN groupadd -g 1001 -f vv8; \
    useradd -u 1001 -g 1001 -s /bin/bash -m vv8
ENV PATH="${PATH}:/home/vv8/.local/bin"

WORKDIR /app
RUN chown -R vv8:vv8 /app

COPY --chown=vv8:vv8 --from=postprocessor artifacts /app/post-processors
COPY --chown=vv8:vv8 --from=vv8 /artifacts/ /artifacts/

VOLUME /workdir

USER vv8

# Add working dir to python path
ENV PYTHONPATH "${PYTHONPATH}:/app"

# Install python modules
COPY --chown=vv8:vv8 ./requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --upgrade -r ./requirements.txt
COPY ./Third-Party-Library-Names /app/Third-Party-Library-Names
ENV THIRD_PARTY_LIBRARY_NAMES_FILE=/app/Third-Party-Library-Names

# Copy app
COPY --chown=vv8:vv8 ./log_parser_worker ./log_parser_worker

CMD celery -A log_parser_worker.app worker -Q log_parser -l INFO -c ${CELERY_CONCURRENCY} -Ofair --max-tasks-per-child 1 -n lg_parser_worker@%h
