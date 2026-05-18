Set-Location $PSScriptRoot\..
poetry run uvicorn api_rowboat.app.main:app --reload --host 127.0.0.1 --port 8000
