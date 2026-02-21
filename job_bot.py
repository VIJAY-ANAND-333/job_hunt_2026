import requests
import os
import json

# Configuration
ADZUNA_ID = os.getenv('ADZUNA_ID')
ADZUNA_KEY = os.getenv('ADZUNA_KEY')
DISCORD_WEBHOOK = os.getenv('DISCORD_WEBHOOK')

def fetch_jobs(location):
    """Fetches the latest DevOps jobs for a specific location."""
    # Using 'where' parameter for specific locations
    url = (f"https://api.adzuna.com/v1/api/jobs/in/search/1?"
           f"app_id={ADZUNA_ID}&app_key={ADZUNA_KEY}&results_per_page=30"
           f"&what=devops&where={location}&content-type=application/json")
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json().get('results', [])
    except Exception as e:
        print(f"Error fetching jobs for {location}: {e}")
        return []

def send_to_discord(job):
    """Sends a formatted alert to your Discord channel."""
    data = {
        "embeds": [{
            "title": f"🚀 New Job: {job['title']}",
            "description": (f"**Company:** {job['company']['display_name']}\n"
                            f"**Location:** {job['location']['display_name']}\n"
                            f"**Keywords Matched:** AWS, K8s, Cloud"),
            "url": job['redirect_url'],
            "color": 5814783  # Nice Blue/Purple color
        }]
    }
    requests.post(DISCORD_WEBHOOK, json=data)

def main():
    # Targeted locations
    locations = ['chennai', 'bengaluru', 'remote']
    # Your preferred tech stack
    keywords = ['aws', 'kubernetes', 'docker', 'terraform', 'cicd', 'devops', 'cloud']
    
    # Load seen jobs to avoid spam
    if os.path.exists('seen_jobs.txt'):
        with open('seen_jobs.txt', 'r') as f:
            seen_ids = set(f.read().splitlines())
    else:
        seen_ids = set()

    new_ids = []
    
    for loc in locations:
        print(f"Scanning for roles in: {loc}...")
        jobs = fetch_jobs(loc)
        
        for job in jobs:
            job_id = str(job['id'])
            if job_id not in seen_ids:
                # Combine title and description for a thorough keyword check
                content = (job.get('title', '') + " " + job.get('description', '')).lower()
                
                if any(tech in content for tech in keywords):
                    send_to_discord(job)
                    seen_ids.add(job_id)
                    new_ids.append(job_id)

    # Update seen_jobs.txt so we don't alert twice
    if new_ids:
        with open('seen_jobs.txt', 'a') as f:
            for jid in new_ids:
                f.write(f"{jid}\n")
        print(f"Successfully found and alerted {len(new_ids)} new jobs.")
    else:
        print("No new matching jobs found in this run.")

if __name__ == "__main__":
    main()