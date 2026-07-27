from  ghcr.io/anomalyco/opencode:1.17.14

ENV PATH="$PATH:/root/.local/bin/"

RUN apk update && apk add --no-cache go git curl uv python3 ripgrep \
  py3-pip python3-dev build-base graphviz graphviz-dev
RUN uv tool install graphifyy
RUN /root/.local/bin/graphify opencode install
