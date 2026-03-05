#!/bin/bash
# Setup script for Local Voice Skill

set -e

echo "🎤 Setting up Local Voice Skill for OpenClaw..."
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo "📋 Checking prerequisites..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 not found${NC}"
    echo "  Install from: https://www.python.org/downloads/"
    exit 1
fi
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✓${NC} Python $PYTHON_VERSION found"

# Check FFmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo -e "${YELLOW}⚠ FFmpeg not found${NC}"
    echo "  Install:"
    echo "    Linux:   sudo apt install ffmpeg"
    echo "    macOS:   brew install ffmpeg"
    echo "    Windows: choco install ffmpeg"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo -e "${GREEN}✓${NC} FFmpeg found"
fi

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}⚠ Docker not found${NC}"
    echo "  Kokoro TTS requires Docker"
    echo "  Install from: https://www.docker.com/get-started/"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo -e "${GREEN}✓${NC} Docker found"
fi

# Check OpenClaw
if ! command -v openclaw &> /dev/null; then
    echo -e "${YELLOW}⚠ OpenClaw not found in PATH${NC}"
    echo "  Make sure OpenClaw is installed and accessible"
fi

echo ""
echo "📦 Installing Python dependencies..."

# Install Python packages
pip3 install --quiet faster-whisper pyav requests 2>/dev/null || {
    echo -e "${RED}✗ Failed to install Python packages${NC}"
    exit 1
}

echo -e "${GREEN}✓${NC} Python dependencies installed"
echo ""

# Install Python packages with progress visible
echo "  - faster-whisper (STT)"
pip3 install faster-whisper --quiet
echo "  - pyav (audio processing)"
pip3 install pyav --quiet
echo "  - requests (HTTP client)"
pip3 install requests --quiet

echo ""
echo "📂 Setting up skill directory..."

# Get OpenClaw skills directory
SKILLS_DIR="$HOME/.openclaw/skills/local-voice"
mkdir -p "$SKILLS_DIR/src"
mkdir -p "$SKILLS_DIR/models"
mkdir -p "$SKILLS_DIR/audio/temp"

# Copy files
echo "  - Copying skill files..."
cp SKILL.md CONFIG.md README.md "$SKILLS_DIR/"
cp -r src/* "$SKILLS_DIR/src/"

echo -e "${GREEN}✓${NC} Skill files copied"
echo ""

# Test Kokoro TTS connection
echo "🔌 Testing Kokoro TTS connection..."
if curl -s http://localhost:8880/v1/audio/voices > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Kokoro TTS is running on port 8880"
else
    echo -e "${YELLOW}⚠${NC} Kokoro TTS not responding on port 8880"
    echo "  Make sure Docker container is running:"
    echo "    docker run --gpus all -p 8880:8880 ghcr.io/remsky/kokoro-fastapi-gpu:latest"
    echo ""
fi

# Install skill in OpenClaw
echo ""
echo "🔧 Installing skill in OpenClaw..."
if command -v openclaw &> /dev/null; then
    openclaw skills install "$SKILLS_DIR" 2>/dev/null || {
        echo -e "${YELLOW}⚠${NC} Could not auto-install skill"
        echo "  Install manually with:"
        echo "    openclaw skills install $SKILLS_DIR"
    }
else
    echo -e "${YELLOW}⚠${NC} OpenClaw not found in PATH"
    echo "  Install skill manually with:"
    echo "    openclaw skills install $SKILLS_DIR"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Test STT:  cd $SKILLS_DIR/src && python3 stt.py test_audio.wav"
echo "  2. Test TTS:  python3 tts.py 'Hello world!' output.mp3 af_bella"
echo "  3. Test integration: python3 integration.py"
echo ""
echo "Configuration:"
echo "  - Edit $SKILLS_DIR/CONFIG.md"
echo "  - Or set environment variables (see CONFIG.md)"
echo ""
echo "Documentation:"
echo "  - Read $SKILLS_DIR/README.md"
echo ""
echo -e "${GREEN}✓${NC} Ready to use!"
