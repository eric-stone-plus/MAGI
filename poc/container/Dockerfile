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
# 第一层:版本稳定/已验证的包。opencode/claude 的平台二进制由 postinstall 安装,
# 必须正常装(不带 --ignore-scripts);omp 只需要 bun 运行时,保持 --ignore-scripts。
RUN npm install -g --ignore-scripts \
      bun \
      @mimo-ai/cli \
      @oh-my-pi/pi-coding-agent \
      @kilocode/cli \
 && npm install -g \
      @anthropic-ai/claude-code \
 && npm cache clean --force

# 第二层:版本与宿主钉死(容器内实测踩过漂移坑:codewhale 0.9.2 的 provider
# 解析与宿主 0.8.66 行为不同,直接打挂 Party A lane)。单独成层,改版本号
# 不必重装第一层。opencode 钉宿主同款 1.18.5。
RUN npm install -g --ignore-scripts codewhale@0.8.66 \
 && npm install -g opencode-ai@1.18.5 \
 && npm cache clean --force

# bun 单独一层正常装:其 npm 包要跑 postinstall 放置平台二进制。
# 独立成层,改动时不必重装上面全部 CLI(上一层残留的 shim 会被这里覆盖)。
RUN npm install -g bun && npm cache clean --force

# codewhale 首次运行时才下载平台二进制到包目录;以 root 预热,
# 避免 node 用户运行期写 /usr/local 触发 EACCES(Party A lane 全灭)
RUN codewhale-tui --version

# procps:QUINTE 的 worker 存活检查 shell 到 `ps -p <pid>`(src/run.rs process_alive);
# slim 基础镜像不带 ps,缺失会让父进程秒判 "worker is not alive" 并杀掉整轮 run。
RUN apt-get update \
 && apt-get install -y --no-install-recommends procps \
 && rm -rf /var/lib/apt/lists/*

COPY --from=quinte-build /src/target/release/quinte /usr/local/bin/quinte
COPY entrypoint.sh /usr/local/bin/seat-entrypoint.sh
RUN chmod +x /usr/local/bin/seat-entrypoint.sh

# node:22-bookworm-slim 自带 uid 1000 的 node 用户,直接复用
USER node
ENV HOME=/home/node

# /config/policy.json(只读挂载)/ /input(brief 只读)/ /state(席位 QUINTE_HOME)/
# /artifacts(输出)/ /cred/*(凭证只读挂载,entrypoint 拷入 $HOME)
ENTRYPOINT ["/usr/local/bin/seat-entrypoint.sh"]
