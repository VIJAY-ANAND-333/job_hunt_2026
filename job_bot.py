import requests
import os
import json

# Configuration
ADZUNA_ID = os.getenv('ADZUNA_ID')
ADZUNA_KEY = os.getenv('ADZUNA_KEY')
DISCORD_WEBHOOK = os.getenv('DISCORD_WEBHOOK')

def fetch_jobs():
    # Searching for 'DevOps' in India, sorted by newest
    url = f"https://api.adzuna.com/v1/api/jobs/in/search/1?app_id={ADZUNA_ID}&app_key={ADZUNA_KEY}&results_per_page=20&what=devops&content-type=application/json"
    response = requests.get(url).json()
    return response.get('results', [])

def send_to_discord(job):
    data = {
        "embeds": [{
            "title": f"🚀 New Job: {job['title']}",
            "description": f"**Company:** {job['company']['display_name']}\n**Location:** {job['location']['display_name']}",
            "url": job['redirect_url'],
            "color": 5814783
        }]
    }
    requests.post(DISCORD_WEBHOOK, json=data)

def main():
    jobs = fetch_jobs()
    
    # Load seen jobs to avoid spam
    if os.path.exists('seen_jobs.txt'):
        with open('seen_jobs.txt', 'r') as f:
            seen_ids = set(f.read().splitlines())
    else:
        seen_ids = set()

    new_ids = []
    for job in jobs:
        if job['id'] not in seen_ids:
            # Filter for your specific tech stack
            desc = job['description'].lower()
            if any(tech in desc for tech in ['aws', 'kubernetes', 'docker', 'terraform']):
                send_to_discord(job)
                new_ids.append(job['id'])

    # Update seen jobs
    with open('seen_jobs.txt', 'a') as f:
        for jid in new_ids:
            f.write(f"{jid}\n")

if __name__ == "__main__":
    main()