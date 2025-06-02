# Azure App Service deployment configuration for container
# Use this file as reference for Azure CLI commands

# Build and deploy commands:

# 1. Build and push to Azure Container Registry
# az acr build --registry <your-registry-name> --image mockpricingagent:latest .

# 2. Deploy to App Service (create if doesn't exist)
# az webapp create --resource-group <resource-group> --plan <app-service-plan> --name <app-name> --deployment-container-image-name <registry-name>.azurecr.io/mockpricingagent:latest

# 3. Configure environment variables
# az webapp config appsettings set --resource-group <resource-group> --name <app-name> --settings OPENAI_API_KEY="<your-api-key>" SECRET_KEY="<your-secret-key>"

# 4. Enable WebSocket support
# az webapp config set --resource-group <resource-group> --name <app-name> --web-sockets-enabled true

# Example complete deployment script:
# RESOURCE_GROUP="mockpricingagent-rg"
# APP_SERVICE_PLAN="mockpricingagent-plan"
# APP_NAME="mockpricingagent-webapp"
# REGISTRY_NAME="mockpricingagentregistry"
# 
# # Create resource group
# az group create --name $RESOURCE_GROUP --location "East US"
# 
# # Create container registry
# az acr create --resource-group $RESOURCE_GROUP --name $REGISTRY_NAME --sku Basic --admin-enabled true
# 
# # Create app service plan (Linux)
# az appservice plan create --name $APP_SERVICE_PLAN --resource-group $RESOURCE_GROUP --sku B1 --is-linux
# 
# # Build and push image
# az acr build --registry $REGISTRY_NAME --image mockpricingagent:latest .
# 
# # Create web app
# az webapp create --resource-group $RESOURCE_GROUP --plan $APP_SERVICE_PLAN --name $APP_NAME --deployment-container-image-name $REGISTRY_NAME.azurecr.io/mockpricingagent:latest
# 
# # Configure settings
# az webapp config appsettings set --resource-group $RESOURCE_GROUP --name $APP_NAME --settings OPENAI_API_KEY="your-openai-key" SECRET_KEY="your-secret-key"
# 
# # Enable WebSockets
# az webapp config set --resource-group $RESOURCE_GROUP --name $APP_NAME --web-sockets-enabled true
