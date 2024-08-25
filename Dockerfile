# Step 1: Use an official Python runtime as a parent image
FROM python:3.11

# python output to docker
ENV PYTHONUNBUFFERED=1

# Step 2: Set the working directory in the container
WORKDIR /app

# Step 3: Copy the requirements file into the container
COPY requirements.txt .

# Step 4: Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get install -y libgl1-mesa-glx

# Step 5: Copy the rest of the application code into the container
COPY . .

# Step 6: Expose the port that the FastAPI app will run on
EXPOSE 8000

# Step 7: Specify the command to run the FastAPI app with Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
