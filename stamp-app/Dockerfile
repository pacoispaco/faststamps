FROM python:3.10-slim-bookworm

# Set the working directory
WORKDIR /app

# Install Pythond dependencies
COPY ./requirements.txt /app
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy the application to the working directory
COPY main.py /app
COPY templates /app/templates
COPY favicon.png /app
COPY faststamps-logo.png /app
COPY faststamps.js /app
COPY logging-conf.yaml /app

# Start the server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80", "--log-config=logging-conf.yaml"]
