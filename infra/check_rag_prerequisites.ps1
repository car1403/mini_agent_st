$ErrorActionPreference = "Stop"

$failures = [System.Collections.Generic.List[string]]::new()

function Test-ServicePort {
    param(
        [Parameter(Mandatory)] [string] $Name,
        [Parameter(Mandatory)] [int] $Port
    )

    $available = Test-NetConnection `
        -ComputerName "127.0.0.1" `
        -Port $Port `
        -InformationLevel Quiet `
        -WarningAction SilentlyContinue

    if ($available) {
        Write-Host "[PASS] $Name port $Port"
        return
    }

    Write-Host "[FAIL] $Name port $Port"
    $failures.Add("$Name is not reachable on port $Port")
}

if (Get-Command docker -ErrorAction SilentlyContinue) {
    Write-Host "[PASS] Docker CLI"
} else {
    Write-Host "[FAIL] Docker CLI"
    $failures.Add("Docker CLI is not available")
}

Test-ServicePort -Name "Ollama" -Port 11434
Test-ServicePort -Name "PostgreSQL/pgvector" -Port 5433
Test-ServicePort -Name "Redis" -Port 6379

try {
    $tags = Invoke-RestMethod -Uri "http://127.0.0.1:11434/api/tags" -TimeoutSec 5
    $modelNames = @($tags.models | ForEach-Object { $_.name })
    foreach ($requiredModel in @("llama3.2", "embeddinggemma")) {
        $installed = $modelNames | Where-Object {
            $_ -eq $requiredModel -or $_ -like "${requiredModel}:*"
        }
        if ($installed) {
            Write-Host "[PASS] Ollama model $requiredModel"
        } else {
            Write-Host "[FAIL] Ollama model $requiredModel"
            $failures.Add("Ollama model $requiredModel is not installed")
        }
    }
} catch {
    Write-Host "[FAIL] Ollama model API"
    $failures.Add("Ollama model list could not be read")
}

if ($failures.Count -gt 0) {
    Write-Host ""
    Write-Host "RAG prerequisites are not ready:"
    $failures | ForEach-Object { Write-Host "- $_" }
    exit 1
}

Write-Host ""
Write-Host "All RAG prerequisites are ready."
