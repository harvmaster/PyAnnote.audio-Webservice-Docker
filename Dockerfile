# Use the official Python image as the base image
FROM python:3.10

# Set the working directory in the container
WORKDIR /app

# Copy the Python scripts and requirements file
COPY app.py main.py requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port that the FastAPI app will run on
EXPOSE 3000

# Command to run the FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3000"]
