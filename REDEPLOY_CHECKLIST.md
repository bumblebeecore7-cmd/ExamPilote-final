# ExamPilote redeploy checklist

The previous repository has no Git remote configured, so it cannot update an
existing Render service until it is connected to GitHub.

1. Create an empty GitHub repository and push this project (do not add either
   `.env` file):

   ```powershell
   git init
   git add .
   git commit -m "Prepare reliable Render deployment"
   git branch -M main
   git remote add origin https://github.com/YOUR-ACCOUNT/ExamPilote.git
   git push -u origin main
   ```

2. In Render, select **New > Blueprint**, then select that repository. Render
   reads `render.yaml` and asks for the two secret values.
3. Enter a working MongoDB Atlas URI for `MONGODB_URI` and a Gemini key for
   `AI_API_KEY`. In Atlas, allow Render to connect through Network Access.
4. Wait for the deploy to finish, then open the `https://<service>.onrender.com`
   URL from the Render dashboard. Verify `/healthz` first, then the home page.

If the old shared URL ends in `trycloudflare.com`, it was a temporary tunnel
and cannot be restored after its local process stops. Share the Render URL
instead.
