# PowerShell launcher for FastAPI backend in Antigravity
$EnvPath = "$env:USERPROFILE\.conda\envs\reslens\python.exe"
$FallbackPath = "C:\ProgramData\miniconda3\envs\reslens\python.exe"
$SecondaryEnvPath = "$env:USERPROFILE\.conda\envs\resume_nlp\python.exe"

if (Test-Path $EnvPath) {
    $PythonExe = $EnvPath
} elseif (Test-Path $FallbackPath) {
    $PythonExe = $FallbackPath
} elseif (Test-Path $SecondaryEnvPath) {
    $PythonExe = $SecondaryEnvPath
} else {
    $PythonExe = "python"
}

Write-Host "Starting FastAPI backend using: $PythonExe" -ForegroundColor Cyan
& $PythonExe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
