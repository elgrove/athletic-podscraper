FROM python:3.9-bullseye

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /usr/src/app

# Install poetry separated from system interpreter
ENV POETRY_VERSION=1.4.0
ENV POETRY_VENV=/opt/poetry-venv
RUN python3 -m venv $POETRY_VENV \
    && $POETRY_VENV/bin/pip install -U pip setuptools \
    && $POETRY_VENV/bin/pip install poetry==${POETRY_VERSION}

# Add `poetry` to PATH
ENV PATH="${PATH}:${POETRY_VENV}/bin"
ENV POETRY_CACHE_DIR=/opt/.cache

# Copy reqs first. If no change to reqs this stage is cached
COPY poetry.lock pyproject.toml ./
RUN poetry check
RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --no-cache --without dev

COPY . .

CMD ["poetry", "run", "python", "main.py"]