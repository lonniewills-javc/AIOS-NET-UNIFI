FROM python:3.12-slim
WORKDIR /app
COPY diagnostics/ /app/
USER 65532:65532
ENV PYTHONUNBUFFERED=1
CMD ["python", "service.py"]
