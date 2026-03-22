# Quick Deployment Commands

Copy-paste these commands in order to deploy to HuggingFace Spaces.

## 1. Stage All Changes
```bash
git add .
```

## 2. Commit Everything
```bash
git commit -m "Stratego game complete: interactive board + Ollama + Mistral 7B"
```

## 3. Add HuggingFace Remote
Replace `YOUR_USERNAME` with your actual HuggingFace username!

```bash
git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/stratego-human-vs-ai
```

## 4. Push to HuggingFace (Triggers Build)
```bash
git push -u hf main
```

## 5. Monitor Build
Watch at: `https://huggingface.co/spaces/YOUR_USERNAME/stratego-human-vs-ai`

Takes: 15-20 minutes (first time only)
- 10 min: Docker build + dependencies
- 5-10 min: Mistral 7B model download

## 6. Once Build Completes
Your game is live at:
```
https://YOUR_USERNAME-stratego-human-vs-ai.hf.space
```

## 7. Test It
Visit the URL above and:
1. See welcome screen
2. Click "Start Game"
3. Config shows Ollama ready
4. Click "Start Game"
5. Click a blue piece
6. See green moves appear
7. Click green destination
8. Piece moves
9. AI responds (2-5 sec)
10. Repeat!

## 8. Share It!
Add to portfolio:
```html
<a href="https://YOUR_USERNAME-stratego-human-vs-ai.hf.space">
  Play Stratego Against AI
</a>
```

---

## For Future Updates

Make changes to code, then:
```bash
git add .
git commit -m "Description of changes"
git push hf main
```

HF Spaces will automatically rebuild and redeploy within 5-10 minutes.

---

## If Build Fails

Click "View logs" in the Space settings page to see error.

Common fixes:
- Missing dependency? Add to `pyproject.toml`
- Syntax error? Fix in Python file
- Dockerfile issue? Check for typos

Then re-push:
```bash
git add .
git commit -m "Fix: [describe fix]"
git push -f hf main
```

---

## Useful Links

Your HF Space: `https://huggingface.co/spaces/YOUR_USERNAME/stratego-human-vs-ai`

Game URL: `https://YOUR_USERNAME-stratego-human-vs-ai.hf.space`

---

That's it! Your game is deployed! 🎉
