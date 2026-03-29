FROM python:3.12-slim

WORKDIR /comp7940-lab

# Stream Python logs immediately (better for `docker logs`)
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code only — mount config.ini at runtime, e.g.:
#   -v /path/to/config.ini:/comp7940-lab/config.ini
COPY chatbot.py ChatGPT_HKBU.py .

CMD ["python", "chatbot.py"]
