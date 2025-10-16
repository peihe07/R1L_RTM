FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Data file will be mounted as volume

EXPOSE 8000

# Create startup script
RUN echo '#!/bin/bash\n\
echo "Waiting for database..."\n\
sleep 10\n\
echo "Loading data into database..."\n\
python load_excel_to_db.py || echo "Data already loaded"\n\
echo "Starting server..."\n\
uvicorn app.main:app --host 0.0.0.0 --port 8000' > /app/start.sh

RUN chmod +x /app/start.sh

CMD ["/app/start.sh"]