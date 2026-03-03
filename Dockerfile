# Use python
FROM python:3.10-slim

# Install the compilation tools and OpenSSL
RUN apt-get update && apt-get install -y \
    gcc \
    libc6-dev \
    libssl-dev \
    make \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy files
COPY . .

# Compile the C library
RUN gcc -fPIC -shared -o back/blockchain/code/blockchain.so \
    back/blockchain/code/block.c \
    back/blockchain/code/sha256.c \
    -lcrypto

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the Flask port
EXPOSE 5001

# Launch the API
CMD ["python3", "back/api/app.py"]
