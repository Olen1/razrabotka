#!/bin/bash

# Запускаем приложение через uv
exec uv run uvicorn --reload --host ${HOST:-0.0.0.0} --port ${PORT:-8000} --log-level debug app.main:app