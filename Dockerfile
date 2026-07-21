# 1. Use Ubuntu to match the exact OS architecture of the GitHub runner
FROM ubuntu:22.04
WORKDIR /app

# 2. Install Python on the bare Ubuntu image
RUN apt-get update && apt-get install -y python3 python3-venv && rm -rf /var/lib/apt/lists/*

# 3. Copy the pre-installed dependencies we downloaded from the artifact!
RUN pip install requirements.txt --no-cache-dir 

# 5. Copy the rest of the application code
COPY . .

EXPOSE 5000

# 6. Run the app
CMD ["python3", "app.py"]
