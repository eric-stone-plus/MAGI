# syntax=docker/dockerfile:1
ARG RUST_IMAGE=rust@sha256:af306cfa71d987911a781c37b59d7d67d934f49684058f96cf72079c3626bfe0
ARG NODE_IMAGE=node@sha256:b04ce4ae4e95b522112c2e5c52f781471a5cbc3b594527bcddedee9bc48c03a0

FROM ${RUST_IMAGE} AS quinte-build
ARG QUINTE_COMMIT
COPY sources/quinte/ /src/quinte/
WORKDIR /src/quinte
RUN test "$(git rev-parse HEAD 2>/dev/null || cat .source-commit)" = "$QUINTE_COMMIT" \
 && cargo build --locked --release \
 && strip target/release/quinte

FROM ${NODE_IMAGE} AS harness-build
RUN npm install -g \
      @mimo-ai/cli@0.1.6 \
      reasonix@1.17.17 \
      @openai/codex@0.145.0 \
 && npm cache clean --force \
 && mimo --version \
 && reasonix --version \
 && codex --version

FROM ${NODE_IMAGE} AS runtime
ARG HERMES_COMMIT
ARG QUINTE_COMMIT
ARG TARGETARCH

ENV HOME=/runtime/home \
    HERMES_HOME=/runtime/hermes-home \
    HERMES_ZERO_WRITE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH=/opt/hermes/bin:/usr/local/bin:/usr/bin:/bin

# Debian package versions are pinned to the selected base snapshot's candidates.
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      ca-certificates=20230311+deb12u1 \
      python3=3.11.2-1+b1 \
      python3-pip=23.0.1+dfsg-1 \
      python3-venv=3.11.2-1+b1 \
      procps=2:4.0.2-3 \
      tini=0.19.0-1+b3 \
 && rm -rf /var/lib/apt/lists/*

COPY sources/hermes/ /src/hermes/
RUN test "$(cat /src/hermes/.source-commit)" = "$HERMES_COMMIT" \
 && python3 -m venv /opt/hermes \
 && /opt/hermes/bin/pip install --require-hashes -r /src/hermes/container-requirements.txt \
 && /opt/hermes/bin/pip install --no-deps /src/hermes \
 && rm -rf /src/hermes /root/.cache

COPY --from=quinte-build /src/quinte/target/release/quinte /usr/local/bin/quinte
COPY --from=harness-build /usr/local/lib/node_modules/ /usr/local/lib/node_modules/
COPY --from=harness-build /usr/local/bin/ /usr/local/bin/
COPY scripts/host/lib/seat_artifacts.py /usr/local/lib/magi/seat_artifacts.py
COPY container/entrypoint.sh /usr/local/bin/magi-seat-entrypoint
RUN chmod 0555 /usr/local/bin/magi-seat-entrypoint /usr/local/lib/magi/seat_artifacts.py \
 && hermes --version \
 && quinte --version \
 && mimo --version \
 && reasonix --version \
 && codex --version

LABEL org.opencontainers.image.title="MAGI independent review seat" \
      org.opencontainers.image.source="https://github.com/eric-stone-plus/MAGI" \
      org.opencontainers.image.hermes.revision="${HERMES_COMMIT}" \
      org.opencontainers.image.quinte.revision="${QUINTE_COMMIT}"

WORKDIR /work
USER node
ENTRYPOINT ["/usr/bin/tini", "--", "/usr/local/bin/magi-seat-entrypoint"]
