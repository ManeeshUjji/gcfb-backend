# PostgreSQL Setup Script for GCFB Dashboard
# This script helps set up the database after PostgreSQL is installed

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host "GCFB Dashboard - Database Setup" -ForegroundColor Cyan
Write-Host ("=" * 60) -ForegroundColor Cyan
Write-Host ""

# Check if PostgreSQL is installed
$psqlPath = Get-Command psql -ErrorAction SilentlyContinue

if (-not $psqlPath) {
    Write-Host "❌ PostgreSQL is not installed or not in PATH" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install PostgreSQL 14+ using one of these methods:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Option 1: Using Chocolatey (Run PowerShell as Administrator):" -ForegroundColor White
    Write-Host "  choco install postgresql14 -y" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Option 2: Download installer from:" -ForegroundColor White
    Write-Host "  https://www.postgresql.org/download/windows/" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Option 3: Using Docker:" -ForegroundColor White
    Write-Host "  docker run --name gcfb-postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres:14" -ForegroundColor Gray
    Write-Host ""
    Write-Host "After installation, update the DATABASE_URL in backend\.env" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

Write-Host "✅ PostgreSQL found at: $($psqlPath.Source)" -ForegroundColor Green
Write-Host ""

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  .env file not found. Creating from .env.example..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "✅ Created .env file. Please update DATABASE_URL with your credentials." -ForegroundColor Green
    Write-Host ""
}

# Check Python dependencies
Write-Host "Checking Python dependencies..." -ForegroundColor Cyan
try {
    python -c "import sqlalchemy, psycopg2, dotenv" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Python dependencies installed" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Installing Python dependencies..." -ForegroundColor Yellow
        python -m pip install -r requirements.txt
    }
} catch {
    Write-Host "❌ Error checking Python dependencies" -ForegroundColor Red
}

Write-Host ""
Write-Host "Database setup ready!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Update backend\.env with your PostgreSQL credentials" -ForegroundColor White
Write-Host "2. Create the database: createdb gcfb" -ForegroundColor White
Write-Host "3. Run the seed script: python data\seed.py" -ForegroundColor White
Write-Host ""
