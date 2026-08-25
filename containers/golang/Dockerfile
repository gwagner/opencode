FROM ghcr.io/anomalyco/opencode:1.18.18

ENV BUN_INSTALL="/root/.bun"
ENV PATH="$PATH:/root/.local/bin/"
ENV PATH="$BUN_INSTALL/bin:$PATH"
ENV PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1
ENV PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH=/usr/bin/chromium
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
ARG GRAPHIFY_VERSION="0.9.48"

RUN apk update && apk add --no-cache go git curl uv python3 ripgrep \
  py3-pip python3-dev build-base graphviz graphviz-dev nodejs npm bash neovim \
  chromium nss freetype harfbuzz ca-certificates ttf-freefont shellcheck ffmpeg
RUN curl -fsSL https://bun.sh/install | bash
RUN uv tool install graphifyy@${GRAPHIFY_VERSION}
RUN uv tool install "graphifyy[sql]"
RUN /root/.local/bin/graphify opencode install

RUN npm install -g tailwindcss @tailwindcss/cli typescript playwright
RUN mkdir -p "$PLAYWRIGHT_BROWSERS_PATH" && npx playwright install ffmpeg
