# 1. Use Ubuntu to match the exact OS architecture of the GitHub runner
FROM ubuntu:22.04
WORKDIR /app

# 2. Install Python on the bare Ubuntu image
RUN apt-get update && apt-get install -y python3 python3-venv

# 3. Copy the pre-installed dependencies we downloaded from the artifact!
COPY .venv/ /app/.venv/

# 4. Update the PATH so the container uses the copied virtual environment
ENV PATH="/app/.venv/bin:$PATH"

# 5. Copy the rest of the application code
COPY . .

EXPOSE 5000

# 6. Run the app

CMD ["python3", "app.py"]
