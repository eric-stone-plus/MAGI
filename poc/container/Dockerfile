# MAGI 席位一体化镜像:quinte(源码构建)+ 五个 harness CLI + claude(cc 仲裁)
# 凭证一律运行时挂载注入,不进镜像层。
ARG QUINTE_REPO=https://github.com/eric-stone-plus/QUINTE.git
ARG QUINTE_REF=main

FROM rust:1-bookworm AS quinte-build
ARG QUINTE_REPO
ARG QUINTE_REF
RUN git clone --depth 1 --branch "$QUINTE_REF" "$QUINTE_REPO" /src
WORKDIR /src
RUN cargo build --release && strip target/release/quinte

FROM node:22-bookworm-slim AS runtime
RUN apt-get update \
 && apt-get install -y --no-install-recommends python3 ca-certificates git \
 && rm -rf /var/lib/apt/lists/*

# 五个 roster harness + claude(cc 仲裁,后端走 MiMo token plan,非 Anthropic 模型)。
# 版本 P0 浮动;定稿前用 npm-shrinkwrap 锁死(参考上游 pi 的供应链纪律)。
RUN npm install -g --ignore-scripts \
      codewhale \
      @mimo-ai/cli \
      opencode-ai \
      @oh-my-pi/pi-coding-agent \
      @anthropic-ai/claude-code \
      @kilocode/cli \
 && npm cache clean --force

COPY --from=quinte-build /src/target/release/quinte /usr/local/bin/quinte
COPY entrypoint.sh /usr/local/bin/seat-entrypoint.sh
RUN chmod +x /usr/local/bin/seat-entrypoint.sh

RUN useradd -m -u 1000 seat
USER seat
ENV HOME=/home/seat

# /config/policy.json(只读挂载)/ /input(brief 只读)/ /state(席位 QUINTE_HOME)/
# /artifacts(输出)/ /cred/*(凭证只读挂载,entrypoint 拷入 $HOME)
ENTRYPOINT ["/usr/local/bin/seat-entrypoint.sh"]
