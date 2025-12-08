FROM python:3.11-slim

WORKDIR /app

# Copy shared protocol module
COPY shared/ /app/shared/

# Copy Bob's code
COPY bob/bob.py /app/

# Make script executable
RUN chmod +x /app/bob.py

# Expose game port
EXPOSE 5555

# Run Bob's server
CMD ["python", "/app/bob.py"]
