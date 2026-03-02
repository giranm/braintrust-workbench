# Reflex production Dockerfile adapted from official example
# Stage 1: init
FROM python:3.12 as init

ARG uv=/root/.local/bin/uv

# Install `uv` for faster package bootstrapping
ADD --chmod=755 https://astral.sh/uv/install.sh /install.sh
RUN /install.sh && rm /install.sh

# Copy local context to `/app` inside container
WORKDIR /app
COPY . .
RUN mkdir -p /app/data /app/uploaded_files

# Create virtualenv which will be copied into final container
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN $uv venv

# Install app requirements and reflex inside virtualenv
RUN $uv pip install -r requirements.txt

# Deploy templates and prepare app
RUN reflex init

# Export static copy of frontend
RUN reflex export --frontend-only --no-zip

# Stage 2: copy artifacts into slim image
FROM python:3.12-slim
WORKDIR /app
RUN adduser --disabled-password --home /app reflex
COPY --chown=reflex --from=init /app /app
RUN mkdir -p /app/.local/share/reflex && chown -R reflex:reflex /app/.local
USER reflex
ENV PATH="/app/.venv/bin:$PATH" PYTHONUNBUFFERED=1

# Needed until Reflex properly passes SIGTERM on backend.
STOPSIGNAL SIGKILL

# Run backend only (nginx will serve frontend)
CMD reflex db migrate 2>/dev/null || true; \
    exec reflex run --env prod --backend-only
