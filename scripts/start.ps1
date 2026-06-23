# TMB — to'liq ishga tushirish (Windows PowerShell)
# Ishlatish:
#   .\scripts\start.ps1 dev
#   .\scripts\start.ps1 staging
param(
    [ValidateSet("dev", "staging")]
    [string]$Mode = "dev"
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

function Require-Docker {
    if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
        Write-Host "XATO: Docker topilmadi." -ForegroundColor Red
        Write-Host "Docker Desktop o'rnating va ishga tushiring: https://docs.docker.com/desktop/setup/install/windows-install/"
        exit 1
    }
    docker info *> $null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "XATO: Docker Desktop ishlamayapti. Ilovani oching." -ForegroundColor Red
        exit 1
    }
}

function Wait-Backend([string[]]$ComposeArgs) {
    Write-Host "Backend kutilyapti..." -ForegroundColor Yellow
    for ($i = 1; $i -le 60; $i++) {
        docker @ComposeArgs exec -T backend python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2)" 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Backend tayyor." -ForegroundColor Green
            return
        }
        Start-Sleep -Seconds 2
    }
    Write-Host "Backend tayyor bo'lmadi." -ForegroundColor Red
    exit 1
}

function Seed-Users([string[]]$ComposeArgs) {
    Write-Host "Demo foydalanuvchilar yuklanmoqda..." -ForegroundColor Yellow
    docker @ComposeArgs exec -T backend python scripts/seed_demo_users.py --i-understand-this-creates-demo-credentials
}

Require-Docker

if ($Mode -eq "dev") {
    Write-Host "=== TMB DEV ===" -ForegroundColor Yellow
    docker compose up -d --build
    Wait-Backend @("compose")
    Seed-Users @("compose")
    Write-Host ""
    Write-Host "Tayyor!" -ForegroundColor Green
    Write-Host "  Frontend: http://localhost:3000"
    Write-Host "  Backend:  http://localhost:8000"
    Write-Host "  Login:    admin.aspect / CenterAdmin#26!"
}
else {
    Write-Host "=== TMB STAGING ===" -ForegroundColor Yellow
    if (-not (Test-Path ".env.staging")) {
        Copy-Item ".env.staging.example" ".env.staging"
        $dbPass = "TmbStaging" + (-join ((48..57) + (65..90) | Get-Random -Count 8 | ForEach-Object { [char]$_ }))
        (Get-Content .env.staging) `
            -replace 'CHANGE_ME_staging_db_password', $dbPass `
            -replace 'CHANGE_ME_32_CHARS_MINIMUM_______', 'dev-staging-secret-32chars-min!!' |
            Set-Content .env.staging
    }
    if (-not (Test-Path "infra/nginx/tls/fullchain.pem")) {
        bash infra/nginx/generate-dev-certs.sh
    }
    $compose = @("compose", "-f", "docker-compose.staging.yml", "--env-file", ".env.staging")
    docker @compose up -d --build
    Wait-Backend $compose
    Seed-Users $compose
    $host = (Select-String -Path .env.staging -Pattern '^PUBLIC_HOST=').Line -replace 'PUBLIC_HOST=', ''
    if (-not $host) { $host = "tamor.staging.local" }
    Write-Host ""
    Write-Host "Tayyor! https://$host" -ForegroundColor Green
    Write-Host "hosts ga qo'shing: 127.0.0.1 $host"
    Write-Host "Login: admin.aspect / CenterAdmin#26!"
}
