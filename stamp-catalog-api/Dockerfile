FROM python:3.10-slim-bookworm

# Set the working directory
WORKDIR /app

# Install Pythond dependencies
COPY ./requirements.txt /app
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy the application to the working directory. We also copy the unit test script so we can run
# that in the Docker container if need be.
COPY main.py /app
COPY .env /app
COPY data/ /app/data/
COPY test_api.py /app

# Start the server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80", "--log-config=logging-conf.yaml"]

