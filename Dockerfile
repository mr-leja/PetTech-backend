FROM python:3.12-slim-bookworm
WORKDIR /app
COPY requirements/ requirements/
RUN pip install --no-cache-dir -r requirements/development.txt
COPY start.py /start.py
EXPOSE 8000
ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["python", "-u", "/start.py"]
