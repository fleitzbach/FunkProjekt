# Find how Python is executed
$pythonExecutable = $(Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $pythonExecutable) {
    $pythonExecutable = $(Get-Command python3 -ErrorAction SilentlyContinue).Source
}
if (-not $pythonExecutable) {
    $pythonExecutable = $(Get-Command py -ErrorAction SilentlyContinue).Source
}
if (-not $pythonExecutable) {
    $pythonExecutable = $(Get-Command py3 -ErrorAction SilentlyContinue).Source
}

# Install Python dependencies
& $pythonExecutable -m pip install -r backend/requirements.txt

# Execute npm install in the frontend folder
Set-Location frontend
npm install
