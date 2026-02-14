# Use Python 3.9
FROM python:3.9

# Set working directory to /app
WORKDIR /app

# Copy the backend requirements first (for caching)
COPY backend/requirements.txt /app/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

# Copy the entire backend folder into /app
COPY backend /app

# Expose port 7860 (Hugging Face Default)
EXPOSE 7860

# Run the app
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]