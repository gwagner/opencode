FROM ghcr.io/anomalyco/opencode:1.18.30

ENV PATH="$PATH:/root/.local/bin/"
ENV PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1
ENV PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH=/usr/bin/chromium
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
ARG GRAPHIFY_VERSION="0.9.48"

ARG USERNAME=opencode
ARG UID=1000
ARG GID=1000

RUN addgroup -g ${GID} ${USERNAME} \
  && adduser \
  -D \
  -u ${UID} \
  -G ${USERNAME} \
  -h /home/${USERNAME} \
  -s /bin/bash \
  ${USERNAME}

# Install core packages
RUN apk update && apk add --no-cache go git curl uv python3 ripgrep \
  py3-pip python3-dev build-base graphviz graphviz-dev nodejs npm bash neovim \
  chromium nss freetype harfbuzz ca-certificates ttf-freefont \
  shellcheck ffmpeg postgresql-client mesa-gles gst-libav openssh-client \
  yq yamllint jq

# Install Graphify
RUN uv tool install graphifyy@${GRAPHIFY_VERSION}
RUN uv tool install "graphifyy[sql]"
RUN /root/.local/bin/graphify opencode install

# Setup hostkey for github.com
RUN mkdir -p -m 0700 ~/.ssh && ssh-keyscan github.com >> ~/.ssh/known_hosts

# Setup in container plugin download
RUN mkdir /opt/plugins
RUN git clone https://github.com/jasnell/opencode-skill-ascii-art-diagrams.git /opt/plugins/opencode-skill-ascii-art-diagrams/

# Setup tailwind
RUN npm install -g tailwindcss @tailwindcss/cli typescript playwright
RUN mkdir -p "$PLAYWRIGHT_BROWSERS_PATH" && npx playwright install 

USER ${USERNAME}
WORKDIR /home/${USERNAME}
