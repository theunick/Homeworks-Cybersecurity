FROM python:3.11-slim

WORKDIR /app

# Copy shared protocol module
COPY shared/ /app/shared/

# Copy Alice's code
COPY alice/alice.py /app/

# Make the script executable
RUN chmod +x /app/alice.py

# Run Alice's client
CMD ["python", "/app/alice.py"]
