# NextRole AI - Azure Deployment & Progress Tracking Setup

## Overview

NextRole AI now integrates **Azure Cosmos DB** for persistent progress tracking, completing the **2+ Azure resources** requirement for Imagine Cup:

1. **Azure OpenAI** — LLM-powered career role analysis
2. **Azure Web App** — Streamlit app hosting (via GitHub CI/CD)
3. **Azure Cosmos DB** — User progress persistence (new)

## Environment Setup

### 1. Create Azure Cosmos DB Instance

```bash
# Login to Azure
az login

# Create resource group (if not exists)
az group create \
  --name nextrole \
  --location eastus

# Create Cosmos DB account
az cosmosdb create \
  --name nextrole-db-account \
  --resource-group nextrole \
  --locations regionName=eastus \
  --kind GlobalDocumentDB

# Create database
az cosmosdb sql database create \
  --account-name nextrole-db-account \
  --resource-group nextrole \
  --name nextrole-db

# Create container for progress tracking
az cosmosdb sql container create \
  --account-name nextrole-db-account \
  --database-name nextrole-db \
  --resource-group nextrole-ai-rg \
  --name progress \
  --partition-key-path "/user_id"
```

### 2. Get Connection String

```bash
# Retrieve connection string
az cosmosdb keys list \
  --name nextrole-db-account \
  --resource-group nextrole \
  --type connection-strings \
  --query "connectionStrings[0].connectionString" -o tsv
```

### 3. Set Environment Variables (Local)

Create or update `.env` file:

```bash
AZURE_OPENAI_API_KEY=<your-azure-openai-key>
AZURE_OPENAI_ENDPOINT=<your-azure-openai-endpoint>
AZURE_OPENAI_DEPLOYMENT_NAME=<your-deployment-name>

COSMOS_CONNECTION_STRING=<paste-connection-string-here>
COSMOS_DATABASE_NAME=nextrole-db
COSMOS_CONTAINER_NAME=progress
```

### 4. Deploy to Azure Web App

Update your GitHub Actions workflow (`.github/workflows/`) to include Cosmos DB env vars:

```yaml
- name: Deploy to Azure Web App
  uses: azure/webapps-deploy@v2
  with:
    app-name: <your-app-name>
    publish-profile: ${{ secrets.AZURE_PUBLISH_PROFILE }}
    images: <your-image>
  env:
    COSMOS_CONNECTION_STRING: ${{ secrets.COSMOS_CONNECTION_STRING }}
    COSMOS_DATABASE_NAME: nextrole-db
    COSMOS_CONTAINER_NAME: progress
```

Or add to **Application Settings** in Azure Web App Portal:

1. Open Azure Portal → App Service → Configuration
2. Add these **Application Settings**:
   - `COSMOS_CONNECTION_STRING` = (paste connection string)
   - `COSMOS_DATABASE_NAME` = `nextrole-db`
   - `COSMOS_CONTAINER_NAME` = `progress`
   - `AZURE_OPENAI_API_KEY` = (existing)
   - `AZURE_OPENAI_ENDPOINT` = (existing)
   - `AZURE_OPENAI_DEPLOYMENT_NAME` = (existing)
3. Click **Save**

## Features Enabled by Cosmos DB

### Progress Tracking
Users can now:
- ✅ View their **career exploration history** (roles analyzed)
- ✅ Track **study phase progress** (% complete, hours spent)
- ✅ Log **skill milestones** (proficiency levels)
- ✅ See **analytics dashboard** (total roles explored, phases completed, skills learned)

### Pages
- **Home** — Career assessment (now tracks role selections)
- **Study Plan** — Learning roadmap with progress sliders
- **My Progress** (NEW) — Career journey dashboard with history and analytics

## Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

Visit `http://localhost:8501` → navigate to **My Progress** to view/track progress.

## Cost Estimation

**Azure Cosmos DB Pricing (East US region):**
- **Database (provisioned):** ~$60–100/month for 400 RU/s
- **Database (serverless):** ~$0.25 per million RUs (good for low traffic)

For a student Imagine Cup project with light traffic, **serverless** is recommended.

## Troubleshooting

### Cosmos DB Connection Not Found
- Check `.env` file has `COSMOS_CONNECTION_STRING`
- Verify connection string from Azure Portal → Cosmos DB Account → Keys
- App will gracefully degrade (progress tracking disabled) if not configured

### Progress Data Not Saving
- Check Azure Portal → Cosmos DB → Data Explorer → `progress` container
- Verify app has Network access to Cosmos DB (if using firewall rules)
- Check app logs for connection errors

### Too Many Requests (429 Error)
- Increase Cosmos DB RU capacity in Azure Portal
- Or reduce concurrent users testing

## Imagine Cup Submission Checklist

- [ ] Cosmos DB instance created and connected
- [ ] App successfully tracks role selections and phase progress
- [ ] **My Progress** page displays user history
- [ ] 3 Azure resources demonstrated:
  - [ ] Azure OpenAI (LLM analysis)
  - [ ] Azure Web App (app hosting)
  - [ ] Azure Cosmos DB (progress persistence)
- [ ] README documents all three Azure services
- [ ] Demo video shows progress tracking in action
- [ ] Pitch deck mentions "Azure-powered career tracking platform"

## Resources

- [Azure Cosmos DB Docs](https://learn.microsoft.com/azure/cosmos-db/)
- [Python SDK for Cosmos DB](https://learn.microsoft.com/python/api/overview/azure/cosmos-db-readme?view=azure-python)
- [Imagine Cup Requirements](https://www.imaginecup.com/)

---

**NextRole AI Team** — Powered by Azure ☁️
