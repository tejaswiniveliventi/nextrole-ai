# Azure Table Storage Setup for NextRole AI

This guide explains how to configure Azure Table Storage for progress tracking in NextRole AI.

## Overview

NextRole AI uses **Azure Table Storage** to persist user career progress data:
- User sessions (skills, career goals, experience level)
- Role selections and career path tracking
- Study phase completion and hours logged
- Skill milestones and proficiency levels

## Prerequisites

1. **Azure Subscription** with an active Storage Account
   - Storage Account Name: `nextrolestorage`
   - Resource Group: `nextrole`

2. **Deployed App** to Azure App Service with GitHub Actions CI/CD

## Step 1: Get Storage Account Connection String

1. Open **Azure Portal** → **Storage Accounts**
2. Select `nextrolestorage` (in resource group `nextrole`)
3. Go to **Security + Networking** → **Access Keys**
4. Copy the **Connection String** under "key1"
   - Format: `DefaultEndpointsProtocol=https;AccountName=nextrolestorage;AccountKey=...;EndpointSuffix=core.windows.net`

## Step 2: Create `progress` Table

1. In the same Storage Account, go to **Data Storage** → **Tables**
2. Click **+ Table** at the top
3. Enter name: `progress`
4. Click **Create**

## Step 3: Configure Web App Application Settings

1. Go to **Azure Portal** → **App Services** → Your NextRole AI web app
2. Click **Configuration** (left sidebar, under Settings)
3. Click **+ New application setting**
4. Add two new settings:

   | Name | Value | Example |
   |------|-------|---------|
   | `AZURE_STORAGE_CONNECTION_STRING` | Connection string from Step 1 | `DefaultEndpointsProtocol=https;AccountName=nextrolestorage;AccountKey=xxx;EndpointSuffix=core.windows.net` |
   | `AZURE_STORAGE_TABLE_NAME` | `progress` | `progress` |

5. Click **Save** at the top
6. When prompted, click **Continue** to restart the app

## Step 4: Verify Local Setup (Optional)

For local development, create a `.env` file in the project root:

```bash
AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name
AZURE_STORAGE_CONNECTION_STRING=your_connection_string_here
AZURE_STORAGE_TABLE_NAME=progress
```

Then install the required package:

```bash
pip install -r requirements.txt
```

Run locally:

```bash
streamlit run app.py
```

## How It Works

### Data Model

All records use **PartitionKey** (user_id) and **RowKey** (type + timestamp) for efficient querying:

**Entity Types:**
- `session`: User profile snapshot (skills, career goal, experience level)
- `role_selection`: When user selects a career role
- `phase_progress`: Study phase completion tracking
- `skill_milestone`: Skill proficiency achievement

### Example Queries

The tracker uses these operations:

1. **Save Session**: `tracker.save_user_session(user_id, {"skills": [...], "career_goal": "..."})`
2. **Save Role**: `tracker.save_role_selection(user_id, role_dict)`
3. **Save Phase Progress**: `tracker.save_phase_progress(user_id, role_name, phase_num, progress_dict)`
4. **Get Progress History**: `tracker.get_user_progress_history(user_id)`
5. **Get Stats**: `tracker.get_user_stats(user_id)`

## Troubleshooting

### "AZURE_STORAGE_CONNECTION_STRING not set" in Logs
**Fix**: Ensure the environment variable is added to Web App Configuration, then restart the app.

### "Failed to initialize Table Storage" Error
**Fix**: Verify the connection string is copied correctly (no extra spaces or line breaks).

### Table Records Not Appearing
**Fix**: 
1. Check that the `progress` table exists in Storage Account
2. Verify user_id is consistent (check logs for actual user ID being used)
3. In Portal: Storage Account → Tables → Select `progress` table to inspect rows

### Local Development Errors
**Fix**: Ensure `.env` file has the correct connection string, and you've run `pip install azure-storage-table`.

## Deployment Notes

- **No manual database setup needed** beyond creating the `progress` table
- Connection string is securely stored in App Service Configuration
- Progress data persists across app restarts
- Table Storage is serverless and scales automatically

## Cost Optimization

Azure Table Storage pricing:
- **Read Operations**: $0.01 per 10,000 transactions
- **Write Operations**: $0.05 per 10,000 transactions
- **Data Storage**: $0.25 per GB

A single user tracking one role with ~20 phases costs < $0.01/month.

## References

- [Azure Table Storage Pricing](https://azure.microsoft.com/en-us/pricing/details/storage/tables/)
- [Azure SDK for Python - Tables](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/tables/azure-data-tables/README.md)
