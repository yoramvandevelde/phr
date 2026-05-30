FROM python:3.12-slim

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync --frozen --no-dev

COPY controller.py .

CMD ["uv", "run", "kopf", "run", "controller.py", "--all-namespaces"]
