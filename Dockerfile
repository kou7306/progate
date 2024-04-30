# Use the official Python image
FROM python

# Set the working directory in the container
WORKDIR /app/backend

# Copy the current directory contents into the container at /app/backend
COPY . /app/backend

# Install any needed packages specified in requirements.txt
RUN pip install -r /app/backend/requirements.txt

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run uvicorn when the container launches
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]