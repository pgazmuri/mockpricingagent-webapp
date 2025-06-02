# PowerShell script for code deployment to Linux App Service
# Run this script from the azure directory

param(
    [string]$AppName = "multiagent-mock-pharmacy",
    [string]$ResourceGroup = "TeamsTelehealth",
    [string]$Location = "East US 2",
    [string]$AppServicePlan = "asp-cvsvirtualcaresupport"  # Must be Linux-based
)

$projectRoot = Split-Path -Parent $PSScriptRoot

Write-Host "Starting code deployment for MockPricingAgent WebApp (Linux)" -ForegroundColor Green
Write-Host "App Name: $AppName" -ForegroundColor Yellow
Write-Host "Resource Group: $ResourceGroup" -ForegroundColor Yellow
Write-Host "Project Root: $projectRoot" -ForegroundColor Yellow

# Check if Azure CLI is installed
try {
    az --version | Out-Null
} catch {
    Write-Error "Azure CLI is not installed. Please install it first."
    exit 1
}

# Login check
Write-Host "Checking Azure login status..." -ForegroundColor Blue
$loginStatus = az account show 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Not logged in to Azure. Please login..." -ForegroundColor Yellow
    az login
}

try {
    # Check if web app exists
    Write-Host "Checking if web app exists..." -ForegroundColor Blue
    $existingApp = az webapp show --resource-group $ResourceGroup --name $AppName

    if ($LASTEXITCODE -ne 0) {
        # Create new Linux web app
        Write-Host "Creating new Linux web app..." -ForegroundColor Blue
        az webapp create `
            --resource-group $ResourceGroup `
            --plan $AppServicePlan `
            --name $AppName `
            --runtime "PYTHON:3.11" `
            --deployment-local-git
    }

    # Set required App Settings
    Write-Host "Configuring app settings..." -ForegroundColor Blue
    az webapp config appsettings set --resource-group $ResourceGroup --name $AppName --settings `
        SCM_DO_BUILD_DURING_DEPLOYMENT="true" `
        WEBSITES_ENABLE_APP_SERVICE_STORAGE="true"

    # Set startup command
    Write-Host "Setting startup command..." -ForegroundColor Blue
    $startupCommand = "gunicorn --worker-class eventlet --chdir src --bind=0.0.0.0:8000 app:app"
    az webapp config set --resource-group $ResourceGroup --name $AppName --startup-file "$startupCommand"

    # Create ZIP package for deployment
    Write-Host "Creating deployment package with 7-Zip..." -ForegroundColor Blue
    $tempZip = "$env:TEMP\mockpricingagent-linux-deploy-NEW.zip"
	Write-Host "Temporary ZIP file path: $tempZip" -ForegroundColor Yellow
    Push-Location $projectRoot

    # Ensure __init__.py exists in src directory
    if (-not (Test-Path "src\__init__.py")) {
        New-Item -Path "src\__init__.py" -ItemType File -Force | Out-Null
    }

    # Check for 7z
    if (-not (Get-Command C:\"Program Files"\7-Zip\7z.exe -ErrorAction SilentlyContinue)) {
        Write-Error "7-Zip (7z.exe) is required but not found in PATH. Please install 7-Zip and ensure it's in your PATH."
        exit 1
    }

    # Remove old zip if exists
    if (Test-Path $tempZip) { Remove-Item $tempZip -Force }

    # Use 7z to create the zip with correct POSIX paths
    & C:\"Program Files"\7-Zip\7z.exe a -tzip $tempZip ./src ./requirements.txt | Out-Null

    Pop-Location

    # Deploy the ZIP file
    Write-Host "Deploying to Azure Linux App Service..." -ForegroundColor Blue
    az webapp deployment source config-zip `
        --resource-group $ResourceGroup `
        --name $AppName `
        --src $tempZip

    Remove-Item $tempZip -Force


    $webappUrl = az webapp show --resource-group $ResourceGroup --name $AppName --query "defaultHostName" --output tsv

    Write-Host "Deployment completed successfully!" -ForegroundColor Green
    Write-Host "Your app is available at: https://$webappUrl" -ForegroundColor Cyan
    Write-Host "Streaming logs (Ctrl+C to stop)..." -ForegroundColor Yellow
    az webapp log tail --resource-group $ResourceGroup --name $AppName

} catch {
    Write-Error "Deployment failed: $($_.Exception.Message)"
    exit 1
}
