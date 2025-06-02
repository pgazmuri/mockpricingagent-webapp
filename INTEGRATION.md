# MockPricingAgent WebApp Integration

This document describes how to integrate and deploy the MockPricingAgent with the Flask web application.

## 📁 Directory Structure

```
mockpricingagent-webapp/
├── src/
│   ├── app.py                 # Main Flask application
│   ├── multi_agent/           # Synced multi-agent code (gitignored)
│   │   ├── .gitignore         # Ignores all files in this directory
│   │   └── [synced .py files] # Copied from C:\Repos\MockPricingAgent
│   ├── static/
│   └── templates/
├── scripts/
│   ├── sync_multi_agent.py    # Script to sync files from external repo
│   └── test_setup.py          # Test script to verify setup
├── azure/
│   ├── deploy.ps1             # PowerShell deployment script
│   └── deploy-commands.sh     # Azure CLI reference commands
├── Dockerfile                 # Container configuration
└── requirements.txt           # Python dependencies
```

## 🔄 Syncing Multi-Agent Code

The multi-agent code is maintained separately in `C:\Repos\MockPricingAgent` and synced into this webapp.

### Manual Sync
```powershell
python scripts\sync_multi_agent.py
```

### What the sync script does:
- Copies all `.py` files from `C:\Repos\MockPricingAgent` to `src\multi_agent\`
- Copies `requirements.txt` if it exists
- Creates/updates `.gitignore` to exclude synced files from version control
- Provides detailed output of the sync process

## 🧪 Testing the Setup

Before deploying, test that everything is configured correctly:

```powershell
python scripts\test_setup.py
```

This will verify:
- Directory structure
- Required files exist
- App configuration is correct
- Sync script can be imported

## 🏃‍♂️ Running Locally

1. Sync the latest multi-agent code:
   ```powershell
   python scripts\sync_multi_agent.py
   ```

2. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

3. Set environment variables:
   ```powershell
   $env:OPENAI_API_KEY="your-api-key"
   $env:SECRET_KEY="your-secret-key"
   ```

4. Run the application:
   ```powershell
   python src\app.py
   ```

5. Open browser to:
   - Main app: http://localhost:5000
   - Terminal interface: http://localhost:5000/terminal

## 🐳 Docker Development

Build and run with Docker:

```powershell
# Build image
docker build -t mockpricingagent-webapp .

# Run container
docker run -p 5000:5000 -e OPENAI_API_KEY="your-key" mockpricingagent-webapp
```

## ☁️ Azure Deployment

### Prerequisites
- Azure CLI installed and logged in
- Docker installed (for local testing)
- Valid Azure subscription

### Quick Deployment

Use the PowerShell script for automated deployment:

```powershell
.\azure\deploy.ps1 -ResourceGroup "mockpricingagent-rg" -AppName "mockpricingagent-webapp" -RegistryName "mockpricingregistry" -OpenAIApiKey "your-api-key"
```

### Manual Deployment

1. Create Azure Container Registry:
   ```bash
   az acr create --resource-group myRG --name myRegistry --sku Basic
   ```

2. Build and push image:
   ```bash
   az acr build --registry myRegistry --image mockpricingagent:latest .
   ```

3. Create App Service:
   ```bash
   az webapp create --resource-group myRG --plan myPlan --name myApp --deployment-container-image-name myRegistry.azurecr.io/mockpricingagent:latest
   ```

4. Configure environment variables:
   ```bash
   az webapp config appsettings set --resource-group myRG --name myApp --settings OPENAI_API_KEY="your-key"
   ```

5. Enable WebSockets:
   ```bash
   az webapp config set --resource-group myRG --name myApp --web-sockets-enabled true
   ```

## 🔧 Architecture

### How it works:
1. Flask app serves the web interface
2. When user accesses `/terminal`, WebSocket connection is established
3. App spawns subprocess running `multi_agent_app.py`
4. Real-time terminal interaction via WebSockets
5. Subprocess supports full multi-agent functionality

### Key Features:
- ✅ **Subprocess support** in Azure App Service containers
- ✅ **Real-time terminal** via WebSockets
- ✅ **Separate codebases** maintained independently
- ✅ **Easy syncing** with automation script
- ✅ **Container deployment** for full compatibility

## 🔍 Troubleshooting

### Sync Issues
- Ensure `C:\Repos\MockPricingAgent` exists and contains `.py` files
- Check file permissions
- Run sync script with Python 3.7+

### Local Testing Issues
- Verify environment variables are set
- Ensure all dependencies are installed
- Check that multi_agent directory has the required files

### Azure Deployment Issues
- Verify Azure CLI is logged in: `az account show`
- Check container registry permissions
- Ensure WebSocket support is enabled
- Monitor App Service logs for errors

## 📝 Development Workflow

1. **Develop multi-agent features** in `C:\Repos\MockPricingAgent`
2. **Test independently** in the original repo
3. **Sync to webapp** using `python scripts\sync_multi_agent.py`
4. **Test integration** locally
5. **Deploy to Azure** when ready

This workflow keeps the codebases separate while providing seamless integration!
