FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    wget \
    bash \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . /app/

# Install Python dependencies
RUN pip install --no-cache-dir -e ".[web]"

# Install Ollama
RUN curl -fsSL https://ollama.ai/install.sh | sh

# Create startup script that handles both Ollama and Streamlit
RUN cat > /app/start.sh << 'EOF'
#!/bin/bash
set -e

echo "================================================"
echo "Starting Stratego Game Server..."
echo "================================================"

# Configure Ollama
export OLLAMA_HOST=0.0.0.0:11434
export OLLAMA_MODELS=/root/.ollama/models

echo "[1/4] Starting Ollama service..."
ollama serve > /tmp/ollama.log 2>&1 &
OLLAMA_PID=$!

# Wait for Ollama to be ready
echo "[2/4] Waiting for Ollama to initialize..."
for i in {1..30}; do
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "✓ Ollama is ready!"
        break
    fi
    echo "  Waiting... ($i/30)"
    sleep 2
done

# Check if Ollama is running
if ! ps -p $OLLAMA_PID > /dev/null; then
    echo "ERROR: Ollama failed to start"
    cat /tmp/ollama.log
    exit 1
fi

# Pull Mistral model (only downloads if not cached)
echo "[3/4] Pulling Mistral 7B model..."
echo "      (This may take 5-10 minutes on first run)"
echo "      (Cached on subsequent runs)"
ollama pull mistral:7b

echo "[4/4] Starting Streamlit application..."
echo "================================================"
echo "✓ Server ready!"
echo "✓ Stratego: http://localhost:8501"
echo "✓ Ollama API: http://localhost:11434"
echo "================================================"

# Start Streamlit
exec streamlit run streamlit_app.py \
    --server.port=8501 \
    --server.address=0.0.0.0 \
    --logger.level=info
EOF

RUN chmod +x /app/start.sh

# Create healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Expose ports
EXPOSE 8501 11434

# Run startup script
CMD ["/app/start.sh"]

