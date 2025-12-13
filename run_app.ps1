# FPL Knowledge Graph Assistant - Startup Script
# Run this script to launch the Streamlit application

Write-Host "=" * 60 -ForegroundColor Magenta
Write-Host "FPL Knowledge Graph Assistant" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Magenta
Write-Host ""

# Navigate to project directory
$projectDir = "d:\Acl Proj MS3\acl_2_FPL"
Set-Location $projectDir

# Check if Neo4j is running
Write-Host "Checking Neo4j connection..." -ForegroundColor Yellow
try {
    $pythonExe = "C:/Users/omarb/AppData/Local/Programs/Python/Python313/python.exe"
    & $pythonExe test_neo4j_connection.py
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "Warning: Neo4j connection test failed!" -ForegroundColor Red
        Write-Host "Make sure Neo4j is running before using the application." -ForegroundColor Yellow
        Write-Host ""
        $continue = Read-Host "Do you want to continue anyway? (y/n)"
        if ($continue -ne "y") {
            exit 1
        }
    }
} catch {
    Write-Host "Warning: Could not test Neo4j connection" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Starting Streamlit application..." -ForegroundColor Green
Write-Host ""
Write-Host "The application will open in your default web browser." -ForegroundColor Cyan
Write-Host "If it doesn't open automatically, navigate to: http://localhost:8501" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the application" -ForegroundColor Yellow
Write-Host "=" * 60 -ForegroundColor Magenta
Write-Host ""

# Launch Streamlit
& $pythonExe -m streamlit run src/ui/app.py --server.port 8501 --server.headless false
