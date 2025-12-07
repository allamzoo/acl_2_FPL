# Setup Script for FPL Graph-RAG

Write-Host "Setting up FPL Graph-RAG project..." -ForegroundColor Green

# Check Python version
$pythonVersion = python --version 2>&1
Write-Host "Python version: $pythonVersion" -ForegroundColor Cyan

# Create virtual environment (optional)
Write-Host "`nCreating virtual environment..." -ForegroundColor Yellow
python -m venv venv

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "`nInstalling dependencies from requirements.txt..." -ForegroundColor Yellow
pip install -r requirements.txt

# Download spaCy model
Write-Host "`nDownloading spaCy English model..." -ForegroundColor Yellow
python -m spacy download en_core_web_sm

# Copy .env.example to .env
if (-not (Test-Path .env)) {
    Write-Host "`nCreating .env file from .env.example..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "Please update .env file with your credentials!" -ForegroundColor Red
}

Write-Host "`nSetup complete! Next steps:" -ForegroundColor Green
Write-Host "1. Install Neo4j Desktop from https://neo4j.com/download/" -ForegroundColor Cyan
Write-Host "2. Create a new database and install GDS plugin" -ForegroundColor Cyan
Write-Host "3. Update .env file with your Neo4j credentials and API keys" -ForegroundColor Cyan
Write-Host "4. Import your FPL data from Milestone 2 into Neo4j" -ForegroundColor Cyan
Write-Host "5. Run the app: streamlit run src/ui/app.py" -ForegroundColor Cyan
