# Stratego Web Game - Deployment Guide
## Deploy to HuggingFace Spaces (FREE)

This guide will deploy your Stratego game with embedded Ollama + Mistral 7B to HuggingFace Spaces.

---

## 📋 Prerequisites

1. **HuggingFace Account** (free): https://huggingface.co/join
2. **Your GitHub credentials** (for git push)
3. **20-30 minutes** (first build downloads Mistral ~4GB)

---

## 🚀 Step-by-Step Deployment

### Step 1: Create HuggingFace Space

1. Go to https://huggingface.co/spaces
2. Click **"Create new Space"**
3. Fill in:
   - **Space name**: `stratego-human-vs-ai`
   - **License**: `openrail` (or your choice)
   - **Space SDK**: `Docker` ← IMPORTANT! Not Streamlit, but **Docker**
4. Click **"Create Space"**
5. You'll see an empty repo at: `https://huggingface.co/spaces/YOUR_USERNAME/stratego-human-vs-ai`

### Step 2: Prepare Your Local Repository

```bash
# Navigate to your project
cd "/d/M.Sc. Digital Technologies/Sem 3/Project/Stratego"

# Initialize git if not done
git init
git add .
git commit -m "Initial commit - Stratego with Ollama integration"

# Add HF Space as remote
git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/stratego-human-vs-ai

# Push to HF Space
git push -u hf main
```

**Replace `YOUR_USERNAME` with your actual HuggingFace username!**

### Step 3: HF Spaces Auto-Build

Once you push:
1. HF Spaces will automatically:
   - Clone your repository
   - Read your `Dockerfile`
   - Build the Docker image
   - Pull the Mistral 7B model
   - Start your app

2. This takes **10-20 minutes** (first time only)

3. Monitor build status at: https://huggingface.co/spaces/YOUR_USERNAME/stratego-human-vs-ai

### Step 4: Access Your Deployed Game

Once build completes (green checkmark ✓):
- **Game URL**: `https://huggingface.co/spaces/YOUR_USERNAME/stratego-human-vs-ai`
- **Direct URL**: `https://YOUR_USERNAME-stratego-human-vs-ai.hf.space`

Share this link on your portfolio! 🎉

---

## 📁 What Gets Deployed

Your Docker container will:
```
1. Install Ollama locally in container
2. Pull Mistral 7B model (4GB - happens once)
3. Start Ollama API server (port 11434)
4. Start Streamlit app (port 8501)
5. Both serve the game at https://your-space-url
```

When a user visits:
- Streamlit loads the interactive board
- Ollama processes AI moves via Mistral 7B
- All happens on the **same server** - no external dependencies!

---

## ✅ Verification Checklist

After deployment:

- [ ] Space shows "RUNNING" status (green)
- [ ] No build errors in logs
- [ ] Can access the game URL
- [ ] Welcome screen loads
- [ ] Can click "Start Game"
- [ ] AI Config shows Ollama available
- [ ] Can start a game
- [ ] Interactive board works
- [ ] AI makes moves (different each time)
- [ ] Game plays smoothly

---

## 🔍 Troubleshooting

### Build Taking Too Long?
- Building + downloading Mistral ~4GB takes 15-20 minutes
- Watch the build logs: click "Open Logs" in Space settings

### "Out of Memory" Error?
- HF Spaces free tier has ~8GB RAM
- Mistral 7B needs ~6-8GB
- Might need to upgrade or use smaller model (Phi 3B)

### Connection Error to Ollama?
- Check that Dockerfile is correct (uses http://localhost:11434)
- Verify app.py uses correct URL (should be default)

### Space Build Failed?
- Click "View logs" to see error
- Common issues: missing dependencies in pyproject.toml
- Re-push with fixes: `git push -u hf main`

---

## 📊 Expected Behavior

**First Visit:**
- 🔄 Ollama initializes (logs show startup)
- ⏳ Image pulls (happens in background)
- ✓ After 2-5 minutes, game becomes responsive

**Subsequent Visits:**
- ⚡ Instant loading (models cached)
- 🎮 Full interaction within seconds

**During Gameplay:**
- 🤖 AI takes 3-5 seconds per move (LLM inference)
- ✅ All moves validated locally
- 📊 Move history and stats display correctly

---

## 🎯 Final Steps After Deployment

1. **Test the URL** on your phone/different device
2. **Add to portfolio**: Link to `https://YOUR_USERNAME-stratego-human-vs-ai.hf.space`
3. **Share with friends** - it's live!
4. **Monitor**: HF Spaces has usage limits - check your Space settings

---

## 🆘 If Something Goes Wrong

If Spaces doesn't work:

### Alternative Option 1: Google Cloud Run
```bash
# Zero-cost option with better specs
gcloud run deploy stratego \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Alternative Option 2: Render.com
- Free tier with persistent storage
- Good for this use case
- https://render.com

### Alternative Option 3: Railway.app
- $5/month free credit
- Easy GitHub integration
- Good performance

---

## 📝 Git Commands Quick Reference

```bash
# After making changes locally:
git add .
git commit -m "Updated game"
git push hf main  # Pushes to HF Space, triggers auto-build

# View deployment logs
git log --oneline

# If needed, reset to last version
git reset --hard HEAD~1
git push -f hf main
```

---

## 🎉 You're Done!

Your Stratego game is now:
- ✅ Publicly accessible 24/7
- ✅ Free to run and host
- ✅ Has real AI (Mistral 7B)
- ✅ No local dependencies
- ✅ Works on any device
- ✅ Ready for your portfolio!

**Next**: Update your portfolio website with the link! 🚀
