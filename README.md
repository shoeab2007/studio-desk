# Shoaib — Studio Desk

Standalone personal business workspace for clients, projects, fees, approvals and follow-ups. No ChatGPT account is required to run this version.

## Status
Source is maintained in this repository; backend integration tests passed locally. NOT yet deployed. Installability and two-device sync require testing at the final HTTPS host. This is a single-owner application, not a multi-user SaaS. No automatic outreach or AI agents are included.

## Run locally (Python 3.12 recommended)
Set STUDIO_PASSWORD securely in your environment (minimum 16 characters), set LOCAL_HTTP=1 for localhost development only, then run `python server.py`. Open http://localhost:8080. Do not commit passwords. The password is shared by your own devices. Sessions expire after 24 hours and after a server restart.

## Deploy independently
1. Create a private GitHub repository named studio-desk and upload the contents of this directory, including the hidden .github directory. Do not upload personal backups or the data directory.
2. Use a Docker-capable host with HTTPS and a persistent disk. Build from the supplied Dockerfile.
3. Set STUDIO_PASSWORD through the hosting provider's secret settings. Do NOT set LOCAL_HTTP in production.
4. Mount persistent storage at /data, writable by container UID 10001. Run exactly one replica: SQLite and sessions are intentionally single-server. Set PORT if the host requires it (default 8080).
5. Open the HTTPS address, sign in, add a test record, and sign in on your second device. Records refresh every 15 seconds while no edit dialog is open.
6. Verify persistence through a server restart and export a JSON backup before entering real client records. Back up /data/studio.db using your host's disk/database backup facilities.

GitHub stores source and runs tests; GitHub Pages cannot run this Python backend. The host and persistent storage are separate services and may have charges. No host account has been provisioned.

## Install on phone and laptop
After HTTPS deployment, open the site in Chrome on Android and use its Install app / Add to home screen menu. On desktop Chrome or Edge, use the app install control. Installation availability depends on the browser. The manifest and app icons are included. This version is online-only: no offline cache or background sync is claimed.

## Move from the original Studio Desk
In the old app, use Backup → Export full backup. Sign into this version and use Backup → Restore backup. Restoring replaces the shared workspace after confirmation. Export existing server records first. CSV is for spreadsheets and cannot restore checkpoints.

## Sync and failure behavior
Edits save to the server. Confirm the status says Saved to server or Synced. Conflicting edits return an error instead of silently replacing newer data. If a save fails, edits remain in memory: export a JSON backup before reloading. Reload the latest server state and manually reconcile your changes; don't blindly restore a stale backup. Polling pauses during edits and pending saves. No data is stored in GitHub. Signed-out users cannot read the records API. The empty application shell is public; all records require authentication. Use only on trusted devices.

## Tests
Run `python -m unittest test_server -v`.
Tests cover unauthorized access, bad passwords, request header protection, successful login, read/write, stale-revision rejection, invalid payment rejection and logout. Frontend syntax was checked separately. Live HTTPS, installation and cross-device UI tests remain deployment checks.
