FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x dashboard/start.sh

# HF Spaces uses port 7860
EXPOSE 7860

CMD ["bash", "dashboard/start.sh"]
