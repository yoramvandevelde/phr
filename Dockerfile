FROM python:3.12-slim

RUN adduser --disabled-password --gecos "" appuser

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync --frozen --no-dev

COPY controller.py .

USER appuser
CMD ["uv", "run", "kopf", "run", "controller.py", "--all-namespaces"]
