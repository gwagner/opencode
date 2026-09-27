FROM node:22-bookworm-slim

ARG USERNAME=node
ARG OPENCODE_VERSION=2.0.15

# RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | tee /etc/apt/keyrings/githubcli-archive-keyring.gpg > /dev/null

RUN (type -p wget >/dev/null || (apt update && apt install wget -y)) \
	&& mkdir -p -m 755 /etc/apt/keyrings \
	&& out=$(mktemp) && wget -nv -O$out https://cli.github.com/packages/githubcli-archive-keyring.gpg \
	&& cat $out | tee /etc/apt/keyrings/githubcli-archive-keyring.gpg > /dev/null \
	&& chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg \
	&& mkdir -p -m 755 /etc/apt/sources.list.d \
	&& echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | tee /etc/apt/sources.list.d/github-cli.list > /dev/null

RUN apt-get update && apt-get install -y --no-install-recommends \
  bash \
  ca-certificates \
  curl \
  git \
  openssh-client \
  gh \
  && rm -rf /var/lib/apt/lists/*

RUN npm install -g @openchamber/web @opencode/cli
RUN npm list -g @opencode/cli

USER ${USERNAME}

WORKDIR /home/${USERNAME}

EXPOSE 3000

ENV OPENCODE_HOST=http://opencode:4096
ENV OPENCODE_SKIP_START="true"

ENV OPENCHAMBER_HOST=0.0.0.0
ENV OPENCODE_SKIP_START=true

CMD ["openchamber", "--foreground", "--port", "3000"]
