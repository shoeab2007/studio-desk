# Studio Desk — Google edition

## Ready now
- Native spreadsheet: https://docs.google.com/spreadsheets/d/1XR4TTzxT5zkNootj3GP55ofsWrY3Ha7hjCvHJ4npIqM/edit
- Complete dashboard: Index.html
- Apps Script backend: Code.gs
- Deployment manifest: appsscript.json

The web app is NOT deployed yet. This version uses Google account authentication, not the Python edition's password. The Python/Docker edition remains in the repository as an alternative.

## One-time setup (use a laptop)
1. Open the spreadsheet above while signed into the Google account that owns it.
2. Choose Extensions → Apps Script.
3. Replace the default Code.gs content with all of this folder's Code.gs.
4. Add an HTML file called Index. Paste all of Index.html into it.
5. In Project Settings, enable showing appsscript.json in the editor. Replace that file with this folder's appsscript.json.
6. Save the project as Studio Desk.
7. Choose Deploy → New deployment → Web app. Set Execute as: Me. Set Who has access: Only myself. Do NOT choose Anyone. Deploy and complete Google's authorisation for this script you own. The script needs Sheets access, read-only Drive access to check file ownership, and your signed-in email.
8. Copy the deployment URL ending in /exec. Open it while signed into the same Google account. The dashboard should say Synced with Google Sheets.
9. Add one test project and check that it appears in Projects. Open the same URL on your phone, signed into the same account; refresh or wait up to one minute. Check that edits appear on both devices before adding real business data.
10. Bookmark the URL on your laptop and add a browser shortcut on your phone. This is an online web app, not an Android APK or offline PWA.

If Apps Script is unavailable from the mobile Sheets app, use a laptop browser. Do not paste passwords, OAuth tokens, or authorisation codes into chat.

## Data safety and scope
Keep the spreadsheet and script private. The script additionally checks that the signed-in user owns the spreadsheet and fails closed if it cannot identify the user. Authorise and open it using the same owner account. Team and client sharing are not enabled.

Use the dashboard to edit Projects. Do not rename columns. Checkpoints are encoded as a JSON list in the last column. Fees and dates are handled by the dashboard; the sheet is a storage view. Direct sheet edits can cause validation errors. Simultaneous Apps Script saves use a lock and content fingerprint: a stale save is rejected, not silently applied. A direct spreadsheet edit during a save is not covered by this lock, so avoid editing the sheet itself while using the app.

Edits save immediately; the active page checks for changes once a minute. Polling pauses during edits or unsaved changes. After an error, export your unsaved JSON backup before refreshing, then reconcile with the latest data. Imports replace existing shared records after confirmation. Do not blindly restore an old backup over newer work. Export backups weekly. Current application limit: 1,000 projects; Google usage quotas also apply.

Existing local Studio Desk records can be moved using Backup → Export full backup in the old app, then Restore backup in this Google app. No existing records were migrated automatically. No client emails, messages, invoices or Drive project folders are automatically created by this version.

## Updating code later
Update the corresponding Apps Script files, then use Deploy → Manage deployments → Edit → New version. Keep the same deployment so your bookmark remains valid.

## Verification
Code syntax and offline validation tests were run. Live Google authorisation, Sheet read/write, deployed UI and two-device testing must be completed after the user-owned deployment. Spreadsheet tabs were verified through the Google API; a Google-rendered visual check was unavailable in the current browser session.
