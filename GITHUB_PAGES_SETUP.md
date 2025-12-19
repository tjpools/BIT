# GitHub Pages Setup Instructions

## Quick Setup (One-Time)

Your workflow is configured! Now enable GitHub Pages:

### Step 1: Enable GitHub Pages

1. Go to: **https://github.com/tjpools/BIT/settings/pages**

2. Under "Build and deployment":
   - **Source**: Select "Deploy from a branch"
   - **Branch**: Select "gh-pages" and "/ (root)"
   - Click **Save**

### Step 2: Trigger First Deployment

Option A - Push triggers it automatically (already done!)
Option B - Manual trigger:
1. Go to: **https://github.com/tjpools/BIT/actions**
2. Click "Update BMNR Tracker" workflow
3. Click "Run workflow" → "Run workflow"

### Step 3: Wait 1-2 Minutes

GitHub will build and deploy your site.

## 🌐 Your Live Tracker URL

Once deployed (1-2 minutes), your tracker will be live at:

**https://tjpools.github.io/BIT/**

Bookmark this on your iPhone! 📱

## Features

✅ **Live Dashboard**: View BMNR tracker from any device
✅ **Auto-Updates**: Refreshes hourly via GitHub Actions  
✅ **Mobile-Friendly**: Responsive design works on iPhone
✅ **Always Available**: Hosted on GitHub's CDN

## What Happens Next

1. **First deployment**: ~2 minutes after enabling Pages
2. **Hourly updates**: Every hour, fresh data is fetched
3. **Push updates**: Any time you push changes to main

## Checking Status

- **Actions**: https://github.com/tjpools/BIT/actions
- **Pages Status**: https://github.com/tjpools/BIT/deployments
- **Settings**: https://github.com/tjpools/BIT/settings/pages

## Troubleshooting

If the page doesn't appear after 5 minutes:

1. Check Actions tab for errors
2. Verify gh-pages branch exists
3. Ensure Pages is enabled in Settings
4. Try manual workflow run

---

**Your tracker will be accessible from anywhere with internet! 🚀**
