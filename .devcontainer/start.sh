#!/bin/bash
# Start Ollama server in the background and log output
if command -v ollama >/dev/null 2>&1; then
echo "Starting Ollama server..."
ollama serve > /home/vscode/ollama.log 2>&1 &
else
echo "Ollama not installed (skipping)."
fi
# Wait for Ollama to start (up to 30 seconds)
if command -v ollama >/dev/null 2>&1; then
echo "Waiting for Ollama to be ready..."
for i in {1..30}; do
if curl -s http://localhost:11434/api/tags > /dev/null; then
echo "Ollama server is up after $i seconds."
break
fi
sleep 1
done
fi
# Pull the model if not present
if command -v ollama >/dev/null 2>&1; then
echo "Checking for model llama3.2:3b..."
if ! ollama list | grep -q "llama3.2:3b"; then
echo "Pulling model llama3.2:3b..."
ollama pull llama3.2:3b || {
echo "Warning: Failed to pull model. Check network or logs."
      }
else
echo "Model llama3.2:3b already exists."
fi
fi
# Verify server is running
if command -v ollama >/dev/null 2>&1; then
echo "Verifying Ollama server..."
if curl -s http://localhost:11434/api/tags > /dev/null; then
echo "Ollama server is running on port 11434."
else
echo "Warning: Ollama server failed to start. Check /home/vscode/ollama.log."
fi
fi
# Keep container running
echo "Container is ready."
tail -f /dev/null