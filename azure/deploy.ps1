# PowerShell script for Azure deployment on Windows
# Run this script from the azure directory

param(
    [string]$AppName="mockpricingagent",
    [string]$RegistryName="gazmuricr",
    [string]$Location = "East US",
    [string]$AppServicePlan = "$AppName-plan"
)

# Get the project root directory (parent of azure directory)
$projectRoot = Split-Path -Parent $PSScriptRoot

Write-Host "Starting Azure deployment for MockPricingAgent WebApp" -ForegroundColor Green
Write-Host "App Name: $AppName" -ForegroundColor Yellow
Write-Host "Registry: $RegistryName" -ForegroundColor Yellow
Write-Host "Location: $Location" -ForegroundColor Yellow
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

# Fix permissions on Azure CLI extensions if needed
Write-Host "Checking Azure CLI extension permissions..." -ForegroundColor Blue
try {
    $extensionPath = "$env:USERPROFILE\.azure\cliextensions\authV2"
    if (Test-Path $extensionPath) {
        Write-Host "Fixing permissions on authV2 extension..." -ForegroundColor Yellow
        # Take ownership and grant full control to current user
        icacls $extensionPath /grant "${env:USERNAME}:(OI)(CI)F" /T /Q
    }
} catch {
    Write-Warning "Could not fix extension permissions: $_"
}

try {
    # Create resource group
    Write-Host "Creating resource group..." -ForegroundColor Blue
    #az group create --name $ResourceGroup --location $Location

    # Create container registry
    Write-Host "Creating container registry..." -ForegroundColor Blue
    #az acr create --resource-group $ResourceGroup --name $RegistryName --sku Basic --admin-enabled true

    # Create app service plan (Windows)
    #Write-Host "Creating app service plan..." -ForegroundColor Blue
    #az appservice plan create --name $AppServicePlan --resource-group $ResourceGroup --sku B1 --hyper-v
    
    # Build and push image with Windows platform
    Write-Host "Building and pushing Docker image for Windows..." -ForegroundColor Blue
    Write-Host "Building from directory: $projectRoot" -ForegroundColor Gray
    az acr build --registry $RegistryName --image "mockpricingagent-linux:latest" --file ../Dockerfile $projectRoot
	Exit-PSHostProcess
	#
    # Get ACR credentials
    Write-Host "Getting container registry credentials..." -ForegroundColor Blue
    $acrUsername = az acr credential show --name $RegistryName --query "username" -o tsv
    $acrPassword = az acr credential show --name $RegistryName --query "passwords[0].value" -o tsv

    # Create or update web app
    Write-Host "Checking web app status..." -ForegroundColor Blue
    $existingApp = az webapp show --resource-group WorkshopGenie --name $AppName 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Web app '$AppName' already exists. Skipping creation." -ForegroundColor Yellow
        Write-Host "To recreate, please delete the existing web app first." -ForegroundColor Yellow
    } else {
        # Create new web app with container configuration and windows runtime
        Write-Host "Creating new container-based web app..." -ForegroundColor Blue
        az webapp create `
            --resource-group WorkshopGenie `
            --plan workshopgenie-DEV-plan `
            --name $AppName `
            --deployment-container-image-name "$RegistryName.azurecr.io/mockpricingagent:latest" `
			
        
        # Configure container settings after creation
        Write-Host "Configuring container registry authentication..." -ForegroundColor Blue
        az webapp config container set `
            --resource-group WorkshopGenie `
            --name $AppName `
            --container-image-name "$RegistryName.azurecr.io/mockpricingagent:latest" `
            --container-registry-url "https://$RegistryName.azurecr.io" `
            --container-registry-user $acrUsername `
            --container-registry-password $acrPassword
    }
    
    # Configure app settings
    Write-Host "Configuring app settings..." -ForegroundColor Blue
    
    # Set additional app settings
    Write-Host "Setting app configuration..." -ForegroundColor Blue
    az webapp config appsettings set --resource-group WorkshopGenie --name $AppName --settings `
        WEBSITES_PORT="5000"
    
    # Enable WebSockets
    Write-Host "Enabling WebSocket support..." -ForegroundColor Blue
    az webapp config set --resource-group WorkshopGenie --name $AppName --web-sockets-enabled true

    # Restart the app to apply changes
    Write-Host "Restarting web app..." -ForegroundColor Blue
    az webapp restart --resource-group WorkshopGenie --name $AppName

    # Get the URL
    $webappUrl = az webapp show --resource-group WorkshopGenie --name $AppName --query "defaultHostName" --output tsv
    
    Write-Host "Deployment completed successfully!" -ForegroundColor Green
    Write-Host "Your app is available at: https://$webappUrl" -ForegroundColor Cyan
    Write-Host "Terminal interface: https://$webappUrl/terminal" -ForegroundColor Cyan

} catch {
    Write-Error "Deployment failed: $($_.Exception.Message)"
    exit 1
}

Write-Host "All done! Your MockPricingAgent WebApp is ready!" -ForegroundColor Green
