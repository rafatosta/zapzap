FROM python:3.13-slim
WORKDIR /service
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY backend ./backend
ENV REPORT_DATABASE=/data/reports.sqlite3
RUN mkdir -p /data && chown 65532:65532 /data
VOLUME ["/data"]
USER 65532:65532
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8080", "--proxy-headers"]
