FROM python:3.11-slim

WORKDIR /app

# Copy shared protocol module
COPY shared/ /app/shared/

# Copy Bob's code
COPY bob/bob.py /app/

# Make the script executable
RUN chmod +x /app/bob.py

# Expose the game port
EXPOSE 5555

# Run Bob's server
CMD ["python", "/app/bob.py"]
