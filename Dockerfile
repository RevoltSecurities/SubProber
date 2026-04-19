FROM python:3.13-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libleveldb-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY . /src
WORKDIR /src

RUN pip install --no-cache-dir uv \
    && uv pip install --system --no-cache-dir . \
    && playwright install --with-deps chromium

FROM python:3.13-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libleveldb1d \
    libsnappy1v5 \
    # playwright chromium dependencies
    libnss3 \
    libatk1.0-0t64 \
    libatk-bridge2.0-0t64 \
    libcups2t64 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2t64 \
    libxshmfence1 \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local/lib/python3.13 /usr/local/lib/python3.13
COPY --from=builder /usr/local/bin/subprober /usr/local/bin/subprober
COPY --from=builder /usr/local/bin/playwright /usr/local/bin/playwright
COPY --from=builder /root/.cache/ms-playwright /root/.cache/ms-playwright

ENTRYPOINT ["subprober"]
