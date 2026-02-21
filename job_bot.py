import requests
import os
import json

# Configuration
ADZUNA_ID = os.getenv('ADZUNA_ID')
ADZUNA_KEY = os.getenv('ADZUNA_KEY')
DISCORD_WEBHOOK = os.getenv('DISCORD_WEBHOOK')

def fetch_jobs(location):
    """Fetches the latest DevOps jobs for a specific location."""
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

def send_to_discord(job, matched_keywords):
    """Sends a formatted alert with the specifically matched keywords."""
    # Convert list to a readable string (e.g., "AWS, Kubernetes")
    matches_str = ", ".join([k.upper() for k in matched_keywords])
    
    data = {
        "embeds": [{
            "title": f"🚀 New Job: {job['title']}",
            "description": (f"**Company:** {job['company']['display_name']}\n"
                            f"**Location:** {job['location']['display_name']}\n"
                            f"**Matches:** `{matches_str}`"),
            "url": job['redirect_url'],
            "color": 5814783 
        }]
    }
    requests.post(DISCORD_WEBHOOK, json=data)

def main():
    locations = ['chennai', 'bengaluru', 'remote']
    keywords = ['aws', 'kubernetes', 'docker', 'terraform', 'cicd', 'devops', 'cloud', 'datadog', 'ansible']
    
    if os.path.exists('seen_jobs.txt'):
        with open('seen_jobs.txt', 'r') as f:
            seen_ids = set(f.read().splitlines())
    else:
        seen_ids = set()

    new_ids = []
    
    for loc in locations:
        print(f"Scanning: {loc}...")
        jobs = fetch_jobs(loc)
        
        for job in jobs:
            job_id = str(job['id'])
            if job_id not in seen_ids:
                content = (job.get('title', '') + " " + job.get('description', '')).lower()
                
                # Identify which specific keywords matched
                found_keywords = [k for k in keywords if k in content]
                
                if found_keywords:
                    send_to_discord(job, found_keywords)
                    seen_ids.add(job_id)
                    new_ids.append(job_id)

    if new_ids:
        with open('seen_jobs.txt', 'a') as f:
            for jid in new_ids:
                f.write(f"{jid}\n")
        print(f"Alerted {len(new_ids)} new jobs.")
    else:
        print("No new matches.")

if __name__ == "__main__":
    main()