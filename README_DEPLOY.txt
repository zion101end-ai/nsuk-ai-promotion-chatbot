NSUK AI PROMOTION INTERVIEW CHATBOT — STREAMLIT DEPLOYMENT

FILES
- app.py
- requirements.txt
- assets/nsuk_logo.png
- assets/nsuk_robot.png

DEPLOY USING STREAMLIT COMMUNITY CLOUD
1. Extract this ZIP on your phone or computer.
2. Create/sign in to GitHub and create a NEW repository. For a public demo, do not upload real staff data or private information.
3. Upload app.py, requirements.txt, and the complete assets folder to the ROOT of that repository. The repository should show app.py and requirements.txt at the top level, and assets/ containing both PNG files.
4. Open https://share.streamlit.io and sign in with GitHub.
5. Choose Create app, then select the repository, branch (usually main), and main file path app.py.
6. In Advanced settings / Secrets, add:
NSUK_ADMIN_PASSWORD = "choose-a-strong-private-password"
7. Deploy. Wait for the build to finish. Streamlit will provide a browser URL ending in streamlit.app.

IMPORTANT
- Do not share your GitHub password or administrator password in chat.
- Do not use real staff personal information in a public prototype.
- The SQLite database is stored in the app's local filesystem. Community Cloud local storage should not be treated as permanent or reliable for important records. For real institutional use, use an approved persistent database, access controls, backups, privacy review, and HTTPS.
- This prototype's scoring is rule-based keyword/answer-length assessment, not a trained AI model. It is decision support only; authorised university committees make official promotion decisions.
- If deployment fails, open the app's Manage app / logs panel and share the error text (not passwords or secrets) for troubleshooting.
