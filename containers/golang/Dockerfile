FROM ghcr.io/anomalyco/opencode:1.18.18

ENV BUN_INSTALL="/root/.bun"
ENV PATH="$PATH:/root/.local/bin/"
ENV PATH="$BUN_INSTALL/bin:$PATH"

RUN apk update && apk add --no-cache go git curl uv python3 ripgrep \
  py3-pip python3-dev build-base graphviz graphviz-dev nodejs npm bash neovim
RUN curl -fsSL https://bun.sh/install | bash
RUN uv tool install graphifyy
RUN /root/.local/bin/graphify opencode install

RUN npm install -g tailwindcss @tailwindcss/cli typescript
# RUN npx update-browserslist-db@latest
RUN apk add shellcheck
