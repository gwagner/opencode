FROM node:22-bookworm-slim

ARG USERNAME=node

RUN npm install -g obsidian-headless \
    && npm cache clean --force

RUN apt-get update && apt-get install -y --no-install-recommends \
  bash \
  ca-certificates \
  curl \
  git \
  openssh-client \
  && rm -rf /var/lib/apt/lists/*

# Persistent locations
RUN mkdir -p \
      /vault \
      /home/${USERNAME}/.config \
    && chown -R ${USERNAME}:${USERNAME} \
      /vault \
      /home/${USERNAME}


USER ${USERNAME}

WORKDIR /vault

ENTRYPOINT ["ob"]
