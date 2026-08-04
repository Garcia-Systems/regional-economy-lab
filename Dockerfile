FROM python:3.13-slim

RUN apt-get update && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --uid 1000 lab
WORKDIR /workspace/regional-economy-lab
COPY --chown=lab:lab . .
RUN pip install --no-cache-dir -e '.[dev]'
USER lab
CMD ["regional-sim", "baseline"]

