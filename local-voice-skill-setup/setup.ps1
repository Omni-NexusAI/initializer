# Setup script for Local Voice Skill (Windows PowerShell)

Write-Host "🎤 Setting up Local Voice Skill for OpenClaw..." -ForegroundColor Green
Write-Host ""

# Check Python
Write-Host "📋 Checking prerequisites..."
try {
    $python = Get-Command python -ErrorAction Stop
    $version = python --version 2>&1
    Write-Host "✓ Python $version" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found" -ForegroundColor Red
    Write-Host "  Install from: https://www.python.org/downloads/"
    exit 1
}

# Check FFmpeg
Write-Host "  Checking FFmpeg..."
try {
    $ffmpeg = Get-Command ffmpeg -ErrorAction Stop
    Write-Host "✓ FFmpeg found" -ForegroundColor Green
} catch {
    Write-Host "⚠ FFmpeg not found" -ForegroundColor Yellow
    Write-Host "  Install with: choco install ffmpeg"
    Write-Host "  Or download from: https://ffmpeg.org/download.html"
    $continue = Read-Host "Continue anyway? (y/n)"
    if ($continue -ne "y") {
        exit 1
    }
}

# Check Docker
Write-Host "  Checking Docker..."
try {
    $docker = Get-Command docker -ErrorAction Stop
    Write-Host "✓ Docker found" -ForegroundColor Green
} catch {
    Write-Host "⚠ Docker not found" -ForegroundColor Yellow
    Write-Host "  Install from: https://www.docker.com/get-started/"
    $continue = Read-Host "Continue anyway? (y/n)"
    if ($continue -ne "y") {
        exit 1
    }
}

# Check OpenClaw
Write-Host "  Checking OpenClaw..."
try {
    $openclaw = Get-Command openclaw -ErrorAction Stop
    Write-Host "✓ OpenClaw found" -ForegroundColor Green
} catch {
    Write-Host "⚠ OpenClaw not found in PATH" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "📦 Installing Python dependencies..." -ForegroundColor Cyan

# Install Python packages
Write-Host "  - Installing faster-whisper..."
pip install faster-whisper --quiet

Write-Host "  - Installing pyav..."
pip install pyav --quiet

Write-Host "  - Installing requests..."
pip install requests --quiet

Write-Host "✓ Python dependencies installed" -ForegroundColor Green
Write-Host ""

# Setup skill directory
Write-Host "📂 Setting up skill directory..." -ForegroundColor Cyan

$skillsDir = "$env:USERPROFILE\.openclaw\skills\local-voice"
$srcDir = Join-Path $skillsDir "src"
$modelsDir = Join-Path $skillsDir "models"
$audioDir = Join-Path $skillsDir "audio"
$tempDir = Join-Path $audioDir "temp"

# Create directories
New-Item -ItemType Directory -Force -Path $skillsDir | Out-Null
New-Item -ItemType Directory -Force -Path $srcDir | Out-Null
New-Item -ItemType Directory -Force -Path $modelsDir | Out-Null
New-Item -ItemType Directory -Force -Path $tempDir | Out-Null

# Copy files
Write-Host "  - Copying skill files..."
Copy-Item -Path "SKILL.md", "CONFIG.md", "README.md", "setup.ps1" -Destination $skillsDir -Force
Copy-Item -Path "src\*" -Destination $srcDir -Recurse -Force

Write-Host "✓ Skill files copied" -ForegroundColor Green
Write-Host ""

# Test Kokoro TTS
Write-Host "🔌 Testing Kokoro TTS connection..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8880/v1/audio/voices" -TimeoutSec 5 -UseBasicParsing
    Write-Host "✓ Kokoro TTS is running on port 8880" -ForegroundColor Green
} catch {
    Write-Host "⚠ Kokoro TTS not responding on port 8880" -ForegroundColor Yellow
    Write-Host "  Make sure Docker container is running:"
    Write-Host "    docker run --gpus all -p 8880:8880 ghcr.io/remsky/kokoro-fastapi-gpu:latest"
}

Write-Host ""

# Install skill in OpenClaw
Write-Host "🔧 Installing skill in OpenClaw..." -ForegroundColor Cyan
if ($openclaw) {
    try {
        & openclaw skills install $skillsDir
        Write-Host "✓ Skill installed" -ForegroundColor Green
    } catch {
        Write-Host "⚠ Could not auto-install skill" -ForegroundColor Yellow
        Write-Host "  Install manually with:"
        Write-Host "    openclaw skills install $skillsDir"
    }
} else {
    Write-Host "⚠ OpenClaw not found in PATH" -ForegroundColor Yellow
    Write-Host "  Install skill manually with:"
    Write-Host "    openclaw skills install $skillsDir"
}

Write-Host ""
Write-Host "🎉 Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Test STT:  cd $srcDir; python stt.py test_audio.wav"
Write-Host "  2. Test TTS:  python tts.ps1 'Hello world!' output.mp3 af_bella"
Write-Host "  3. Test integration: python integration.py"
Write-Host ""
Write-Host "Configuration:" -ForegroundColor Cyan
Write-Host "  - Edit $skillsDir\CONFIG.md"
Write-Host "  - Or set environment variables (see CONFIG.md)"
Write-Host ""
Write-Host "Documentation:" -ForegroundColor Cyan
Write-Host "  - Read $skillsDir\README.md"
Write-Host ""
Write-Host "✓ Ready to use!" -ForegroundColor Green
