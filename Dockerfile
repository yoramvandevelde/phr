FROM python:3.12-slim

USER appuser

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync --frozen --no-dev

COPY controller.py .

RUN adduser --disabled-password --gecos "" appuser
CMD ["uv", "run", "kopf", "run", "controller.py", "--all-namespaces"]
