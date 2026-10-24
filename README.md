# GBPUSD Research: automatic hourly reels

One reel an hour, 06:00 to 22:59 London time (17 a day, DST handled), 70 reels in order
(Market Wizards Series 1 to 7). Each run renders the next reel on GitHub's servers and
sends it straight to Instagram. Nothing to download or upload. Progress is kept in state.json.

## Setup (about 15 minutes, once)

### 1. GitHub repo
- Create a repo (public or private) under gbpusdresearch-create, e.g. `gbpusd-reels`.
- Add these files with the exact paths (Add file > Create new file, type the path):
  `reels.py`, `content.json`, `state.json`, `.github/workflows/post.yml`, `.github/workflows/check.yml`
- Settings > Actions > General > Workflow permissions > Read and write permissions > Save.

### 2. Instagram access (the only fiddly part)
- Instagram account must be Business or Creator, linked to a Facebook Page.
- developers.facebook.com > Create App (Business). Add the Instagram product / Graph API use case.
- Graph API Explorer: select your app, get a User token with permissions
  `instagram_basic`, `instagram_content_publish`, `pages_show_list`, `pages_read_engagement`.
- Make it long-lived (Access Token Debugger > Extend), then in Explorer call `me/accounts`.
  Copy the Page `access_token` from the result. A Page token made from a long-lived user token never expires.
- While you are admin of the app and the account, no Meta app review is needed.

### 3. Secrets
Repo > Settings > Secrets and variables > Actions > New repository secret:
- `ACCESS_TOKEN` = the Page token (required)
- `IG_USER_ID` = optional. If you leave it out, the script finds your Instagram ID itself.

### 4. Verify (posts nothing)
Actions tab > "Check connection" > Run workflow. The log should say
`OK: connected to Instagram @...`. If not, the message says exactly what is missing.

### 5. First post
Actions tab > "Post reel" > Run workflow > type 1 in force > Run. Then it runs by itself every hour.

## Good to know
- Hours: change HOUR_FROM / HOUR_TO in post.yml.
- GitHub can start a scheduled run a few minutes late; the script posts at most once per hour.
- A failed run changes nothing: the same reel is retried next hour. No reel is skipped or doubled.
- After reel 70 it stops. Ask Claude for the next series, replace content.json and set next_index to 0 in state.json.
- Cost: GitHub Actions and the Instagram API are free for this use.
