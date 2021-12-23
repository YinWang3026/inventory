FROM python:3.8-slim

# Create working folder and install dependencies
WORKDIR /app
COPY requirements.txt config.py ./
RUN pip install -U pip wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copy the application contents
COPY service/ ./service/

# Switch to a non-root user
RUN useradd --uid 1000 vagrant && chown -R vagrant /app
USER vagrant

# Expose any ports the app is expecting in the environment
ENV FLASK_APP=service:app
ENV PORT 8080
EXPOSE $PORT

ENV GUNICORN_BIND 0.0.0.0:$PORT
# Default parameters that cannot be overridden when Docker Containers run with CLI parameters (docker run).
ENTRYPOINT ["gunicorn"] 
# Sets default parameters that can be overridden when Docker Containers run with CLI parameters (docker run).
CMD ["--log-level=info", "service:app"]
# Aka, when running this image, we will always run gunicorn, followed by some cmds, if not supplied, the above default is used
# Aka running "gunicorn --log-level=info service:app"