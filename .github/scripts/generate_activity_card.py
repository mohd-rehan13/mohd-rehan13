
#!/usr/bin/env python3
import json
import os
import urllib.request
from datetime import date, timedelta
from html import escape

TOKEN = os.environ["GITHUB_TOKEN"]
USERNAME = "mohd-rehan13"
QUERY = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      totalCommitContributions
      contributionCalendar {
        weeks {
          contributionDays { date contributionCount }
        }
      }
    }
  }
}
"""

now = date.today()
variables = {
    "login": USERNAME,
    "from": "2000-01-01T00:00:00Z",
    "to": f"{now.isoformat()}T23:59:59Z",
}
request = urllib.request.Request(
    "https://api.github.com/graphql",
    data=json.dumps({"query": QUERY, "variables": variables}).encode(),
    headers={
        "Authorization": f"bearer {TOKEN}",
        "Content-Type": "application/json",
        "User-Agent": "github-activity-card",
    },
)
with urllib.request.urlopen(request) as response:
    payload = json.load(response)
if payload.get("errors"):
    raise RuntimeError(payload["errors"])

collection = payload["data"]["user"]["contributionsCollection"]
counts = {
    item["date"]: item["contributionCount"]
    for week in collection["contributionCalendar"]["weeks"]
    for item in week["contributionDays"]
}
active = {day for day, count in counts.items() if count > 0}

current = 0
cursor = now
while cursor.isoformat() in active:
    current += 1
    cursor -= timedelta(days=1)

longest = 0
run = 0
start = min(counts) if counts else now.isoformat()
end = max(counts) if counts else now.isoformat()
cursor = date.fromisoformat(start)
last = date.fromisoformat(end)
while cursor <= last:
    if cursor.isoformat() in active:
        run += 1
        longest = max(longest, run)
    else:
        run = 0
    cursor += timedelta(days=1)

commits = collection["totalCommitContributions"]
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="280" viewBox="0 0 900 280" role="img" aria-labelledby="title desc">
<title id="title">GitHub activity statistics for {escape(USERNAME)}</title>
<desc id="desc">Current streak, longest streak, and total commits.</desc>
<defs><linearGradient id="bg" x1="0" x2="1"><stop stop-color="#0f172a"/><stop offset="1" stop-color="#1e293b"/></linearGradient></defs>
<rect width="900" height="280" rx="20" fill="url(#bg)"/>
<text x="45" y="58" fill="#f8fafc" font-family="Arial,sans-serif" font-size="27" font-weight="700">GitHub Activity</text>
<text x="45" y="87" fill="#94a3b8" font-family="Arial,sans-serif" font-size="15">Focused contribution milestones</text>
<g font-family="Arial,sans-serif" text-anchor="middle">
<rect x="45" y="120" width="250" height="105" rx="14" fill="#172554" stroke="#334155"/>
<rect x="325" y="120" width="250" height="105" rx="14" fill="#431407" stroke="#334155"/>
<rect x="605" y="120" width="250" height="105" rx="14" fill="#3f0d32" stroke="#334155"/>
<text x="170" y="155" fill="#93c5fd" font-size="16">CURRENT STREAK</text>
<text x="170" y="201" fill="#f8fafc" font-size="38" font-weight="700">{current}</text>
<text x="170" y="219" fill="#94a3b8" font-size="13">days</text>
<text x="450" y="155" fill="#fdba74" font-size="16">LONGEST STREAK</text>
<text x="450" y="201" fill="#f8fafc" font-size="38" font-weight="700">{longest}</text>
<text x="450" y="219" fill="#94a3b8" font-size="13">days</text>
<text x="730" y="155" fill="#f9a8d4" font-size="16">TOTAL COMMITS</text>
<text x="730" y="201" fill="#f8fafc" font-size="38" font-weight="700">{commits}</text>
<text x="730" y="219" fill="#94a3b8" font-size="13">all time</text>
</g></svg>'''
with open("assets/github-activity.svg", "w", encoding="utf-8") as output:
    output.write(svg)
