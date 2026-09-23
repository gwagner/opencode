FROM node:22-bookworm-slim

ARG USERNAME=openchamber
ARG UID=1000
ARG GID=1000

RUN apt-get update && apt-get install -y --no-install-recommends \
  bash \
  ca-certificates \
  curl \
  git \
  openssh-client \
  && rm -rf /var/lib/apt/lists/*

RUN groupadd --gid ${GID} ${USERNAME} \
  && useradd \
  --uid ${UID} \
  --gid ${GID} \
  --create-home \
  --shell /bin/bash \
  ${USERNAME}

RUN npm install -g @openchamber/web

USER ${USERNAME}

WORKDIR /home/${USERNAME}

EXPOSE 3000

ENV OPENCODE_HOST=http://opencode:4096
ENV OPENCODE_SKIP_START="true"

ENV OPENCHAMBER_HOST=0.0.0.0
ENV OPENCODE_SKIP_START=true

CMD ["openchamber", "--foreground", "--port", "3000"]
