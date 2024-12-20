# Use Python 3.11 base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app
# Create DB directory
RUN mkdir -p /app/.DB

# Copy requirements
COPY pyproject.toml .
COPY src/ .
COPY .streamlit/ .streamlit/

# Install dependencies using the pyproject.toml
RUN pip install -e .

# Expose port 5000
EXPOSE 5000

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run streamlit
CMD ["streamlit", "run", "fontend/main.py", "--server.port", "5000"]
