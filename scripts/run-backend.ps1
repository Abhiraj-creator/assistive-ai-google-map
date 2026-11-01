<#
.SYNOPSIS
Starts the Google ADK API server used by the Next.js UI.

.DESCRIPTION
Creates a project-local virtual environment the first time it runs, installs
the backend dependencies, and serves the agent on http://127.0.0.1:8000.
#>

$ErrorActionPreference = 'Stop'

$projectRoot = Split-Path -Parent $PSScriptRoot
$venvPath = Join-Path $projectRoot '.venv'
$adk = Join-Path $venvPath 'Scripts\adk.exe'
$backendPython = Join-Path $venvPath 'Scripts\python.exe'
$requirements = Join-Path $projectRoot 'google_map_adk\requirements.txt'

$needsInstall = -not (Test-Path $adk)
if (-not $needsInstall) {
    $previousErrorAction = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    & $backendPython -c "import importlib.metadata as m; assert m.version('litellm') == '1.105.1'" 2>$null | Out-Null
    $needsInstall = $LASTEXITCODE -ne 0
    $ErrorActionPreference = $previousErrorAction
}

if ($needsInstall) {
    # Prefer the interpreter the user verified; the `py` launcher may point at
    # an old Windows Store installation.
    $python = Get-Command python -ErrorAction SilentlyContinue
    $pythonArgs = @()
    if (-not $python) {
        $python = Get-Command py -ErrorAction SilentlyContinue
        $pythonArgs = @('-3')
    }
    if (-not $python) {
        throw 'Python 3.11+ is required. Install it from https://www.python.org/downloads/ and run this script again.'
    }

    $pythonPath = $python.Source
    & $pythonPath @pythonArgs -m venv $venvPath
    & (Join-Path $venvPath 'Scripts\pip.exe') install -r $requirements
}

Set-Location $projectRoot
& $adk api_server google_map_adk --host 127.0.0.1 --port 8000
