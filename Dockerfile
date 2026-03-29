FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

ENV PYTHONUNBUFFERED=1

CMD ["sh", "-c", "python inference.py && tail -f /dev/null"]
