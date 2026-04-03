import requests
from bs4 import BeautifulSoup
from enum import Enum


class ImmigrationSource(Enum):
    GENERAL = "general"
    USCIS = "uscis"


class JobLocation(Enum):
    CHICAGO = "Chicago"
    NEW_YORK = "New York"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/146.0.0.0 Safari/537.36"
    )
}

# Free API key from https://www.weatherapi.com (free tier)
WEATHER_API_KEY = "8dec9730999444ffa07144637262803"
WEATHER_LOCATION = "New York"

# Free API from football-data.org (free tier, register for key)
FOOTBALL_API_KEY = "fd9732c68b3c4fa38a6a4033a07d6414"
PREMIER_LEAGUE_ID = "PL"


def get_weather_alerts(location: str = WEATHER_LOCATION) -> list[str]:
    """Fetch current weather conditions and any alerts via weatherapi.com."""
    url = "http://api.weatherapi.com/v1/forecast.json"
    params = {"key": WEATHER_API_KEY, "q": location, "alerts": "yes", "days": 1}
    response = requests.get(url, params=params, headers=HEADERS, timeout=10)
    response.raise_for_status()
    data = response.json()

    results = []

    # Current conditions
    current = data.get("current", {})
    condition = current.get("condition", {}).get("text", "")
    temp_c = current.get("temp_c", "")
    results.append(f"Current weather in {location}: {condition}, {temp_c}°C")

    # Alerts
    alerts = data.get("alerts", {}).get("alert", [])
    if alerts:
        for alert in alerts[:3]:
            results.append(f"ALERT: {alert.get('headline', alert.get('event', ''))}")
    else:
        results.append("No active weather alerts.")

    return results


def get_premier_league_scores() -> list[str]:
    """Fetch latest Premier League match scores via football-data.org."""
    url = f"https://api.football-data.org/v4/competitions/{PREMIER_LEAGUE_ID}/matches"
    headers = {**HEADERS, "X-Auth-Token": FOOTBALL_API_KEY}
    params = {"status": "FINISHED", "limit": 10}
    response = requests.get(url, headers=headers, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    matches = data.get("matches", [])
    if not matches:
        return ["No recent Premier League matches found."]

    scores = []
    for match in matches[-10:]:
        home = match["homeTeam"]["shortName"]
        away = match["awayTeam"]["shortName"]
        score = match["score"]["fullTime"]
        scores.append(f"{home} {score['home']} - {score['away']} {away}")

    return scores


def get_immigration_news(source: ImmigrationSource = ImmigrationSource.GENERAL) -> list[str]:
    """Fetch latest immigration news headlines.

    GENERAL: broad immigration news via Google News RSS.
    USCIS:   USCIS-specific updates via Google News RSS filtered to site:uscis.gov.
    """
    if source == ImmigrationSource.USCIS:
        url = "https://news.google.com/rss/search?q=site:uscis.gov+OR+USCIS+immigration+update&hl=en-US&gl=US&ceid=US:en"
    else:
        url = "https://news.google.com/rss/search?q=immigration+news&hl=en-US&gl=US&ceid=US:en"

    response = requests.get(url, headers=HEADERS, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "xml")

    headlines = []
    for item in soup.find_all("item")[:5]:
        title = item.find("title")
        if title:
            headlines.append(title.get_text(strip=True))

    return headlines or ["No immigration news found."]


def _fetch_linkedin_jobs(role: str, location: str, count: int = 5) -> list[str]:
    """Fetch job listings from LinkedIn guest API for a given role and location (past 24 hours)."""
    url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
    params = {"keywords": role, "location": location, "start": 0, "f_TPR": "r86400"}
    response = requests.get(url, headers=HEADERS, params=params, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    jobs = []
    seen = set()
    for li in soup.find_all("li"):
        title = li.find("h3")
        company = li.find("h4")
        link_tag = li.find("a", class_="base-card__full-link")
        date_tag = li.find("time")
        if not title or not company:
            continue
        title_text = title.get_text(strip=True)
        company_text = company.get_text(strip=True)
        key = (title_text, company_text)
        if key in seen:
            continue
        seen.add(key)
        href = link_tag["href"].split("?")[0] if link_tag else ""
        posted = date_tag.get_text(strip=True) if date_tag else ""
        jobs.append(f"{title_text} @ {company_text} ({posted})\n  {href}")
        if len(jobs) >= count:
            break

    return jobs or [f"No {role} jobs found in {location}."]


def get_linkedin_job_alerts(location: JobLocation = JobLocation.CHICAGO, count: int = 5) -> dict[str, list[str]]:
    """Fetch top N Softwar
    e Engineer and Data Engineer jobs for a given location."""
    loc = location.value
    return {
        "Software Engineer": _fetch_linkedin_jobs("Software Engineer", loc, count=count),
        "Data Engineer": _fetch_linkedin_jobs("Data Engineer", loc, count=count),
    }


if __name__ == "__main__":
    print("=== Weather Alerts ===")
    for line in get_weather_alerts():
        print(f"  {line}")

    print("\n=== Premier League Scores ===")
    for score in get_premier_league_scores():
        print(f"  - {score}")

    print("\n=== Immigration News ===")
    for headline in get_immigration_news():
        print(f"  - {headline}")

    print("\n=== LinkedIn Job Alerts (Chicago) ===")
    jobs = get_linkedin_job_alerts(JobLocation.CHICAGO)
    for role, listings in jobs.items():
        print(f"  [{role}]")
        for j in listings:
            print(f"    - {j}")
