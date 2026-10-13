FROM python:3.14-slim

WORKDIR /app
COPY pyproject.toml uv.lock ./

RUN pip install uv && \
    UV_PYTHON_DOWNLOADS=never uv sync --frozen --no-dev

COPY controller.py .

RUN adduser --disabled-password --gecos "" appuser && \
    chown -R appuser:appuser /app

USER appuser

CMD ["/app/.venv/bin/kopf", "run", "controller.py", "--all-namespaces"]
