"""
Data collection module for GitHub trending repositories
Includes web scraping and API integration
"""

import time
import logging
from typing import List, Dict
import requests
from bs4 import BeautifulSoup
import pandas as pd
from .utils import GitHubAPI, DataManager, get_timestamp

logger = logging.getLogger(__name__)


class GithubTrendingScraper:
    """Scrapes GitHub trending repositories"""
    
    def __init__(self):
        self.base_url = "https://github.com/trending"
        self.api = GitHubAPI()
        self.data_manager = DataManager()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    
    def scrape_trending(self, language: str = "", since: str = "daily") -> List[Dict]:
        """
        Scrape trending repositories
        
        Args:
            language: Programming language filter (e.g., "python", "javascript")
            since: Time range ("daily", "weekly", "monthly")
        
        Returns:
            List of repository dictionaries
        """
        params = {"since": since}
        url = self.base_url
        
        if language:
            url = f"{url}/{language}"
            params["spoken_language_code"] = language
        
        logger.info(f"Scraping GitHub trending: {url}")
        
        try:
            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            repos = self._parse_trending_repos(soup)
            
            logger.info(f"Found {len(repos)} trending repositories")
            return repos
        
        except Exception as e:
            logger.error(f"Scraping failed: {str(e)}")
            return []
    
    def _parse_trending_repos(self, soup: BeautifulSoup) -> List[Dict]:
        """Parse HTML and extract repository information"""
        repos = []
        
        repo_items = soup.find_all("article", class_="Box-row")
        
        for item in repo_items:
            try:
                repo_dict = self._extract_repo_info(item)
                if repo_dict:
                    repos.append(repo_dict)
            except Exception as e:
                logger.warning(f"Error parsing repo item: {str(e)}")
                continue
        
        return repos
    
    def _extract_repo_info(self, item) -> Dict:
        """Extract information from a single repository item"""
        try:
            # Repository name and URL
            repo_link = item.find("h2", class_="h3").find("a")
            repo_name_full = repo_link.get("href").strip("/")
            owner, repo = repo_name_full.split("/")
            url = f"https://github.com{repo_link.get('href')}"
            
            # Description
            desc_elem = item.find("p", class_="col-9")
            description = desc_elem.text.strip() if desc_elem else ""
            
            # Language
            lang_elem = item.find("span", itemprop="programmingLanguage")
            language = lang_elem.text.strip() if lang_elem else "Unknown"
            
            # Stars today
            stars_elem = item.find("span", class_="d-inline-block float-sm-right")
            stars_today = stars_elem.text.strip().split()[0] if stars_elem else "0"
            
            # Total stars
            stars_links = item.find_all("a", class_="Link--muted")
            total_stars = "0"
            total_forks = "0"
            
            for link in stars_links:
                text = link.text.strip()
                if "Star" in link.get_text(strip=True) or any(char.isdigit() for char in text):
                    if "k" in text or "m" in text or any(c.isdigit() for c in text):
                        total_stars = text.split()[0]
                    
            
            repo_dict = {
                "owner": owner,
                "repo_name": repo,
                "full_name": repo_name_full,
                "url": url,
                "description": description,
                "language": language,
                "stars_today": stars_today,
                "total_stars": total_stars,
                "scraped_at": get_timestamp()
            }
            
            return repo_dict
        
        except Exception as e:
            logger.warning(f"Error extracting repo info: {str(e)}")
            return None
    
    def enrich_with_api_data(self, repos: List[Dict]) -> List[Dict]:
        """
        Enrich scraped data with GitHub API information
        
        Args:
            repos: List of repository dictionaries
        
        Returns:
            Enriched repository list
        """
        logger.info("Enriching data with GitHub API...")
        
        enriched = []
        for i, repo in enumerate(repos):
            if i % 10 == 0:
                logger.info(f"Processing {i}/{len(repos)}")
                time.sleep(1)  # Rate limiting
            
            try:
                owner = repo["owner"]
                repo_name = repo["repo_name"]
                
                # Fetch detailed repo info
                details = self.api.get_repo_details(owner, repo_name)
                
                if details:
                    repo.update({
                        "stars": details.get("stargazers_count", 0),
                        "forks": details.get("forks_count", 0),
                        "watchers": details.get("watchers_count", 0),
                        "open_issues": details.get("open_issues_count", 0),
                        "created_at": details.get("created_at", ""),
                        "updated_at": details.get("updated_at", ""),
                        "topics": ",".join(details.get("topics", [])),
                        "license": details.get("license", {}).get("name", "Unknown") if details.get("license") else "Unknown",
                        "is_fork": details.get("fork", False),
                    })
                    
                    # Fetch languages
                    languages = self.api.get_repo_languages(owner, repo_name)
                    if languages:
                        total_bytes = sum(languages.values())
                        repo["primary_language"] = max(languages, key=languages.get) if languages else "Unknown"
                        repo["language_diversity"] = len(languages)
                    
                    enriched.append(repo)
            
            except Exception as e:
                logger.warning(f"API enrichment failed for {owner}/{repo_name}: {str(e)}")
                enriched.append(repo)
        
        return enriched


def collect_github_trending_data(languages: List[str] = None, since: str = "daily") -> pd.DataFrame:
    """
    Main function to collect and enrich GitHub trending data
    
    Args:
        languages: List of programming languages to scrape
        since: Time range for trending
    
    Returns:
        DataFrame with collected data
    """
    if languages is None:
        languages = ["python", "javascript", "java", "go", "rust", "typescript"]
    
    scraper = GithubTrendingScraper()
    all_repos = []
    
    for lang in languages:
        logger.info(f"Scraping {lang} repositories...")
        repos = scraper.scrape_trending(language=lang, since=since)
        
        if repos:
            repos = scraper.enrich_with_api_data(repos)
            all_repos.extend(repos)
        
        time.sleep(2)  # Be respectful to servers
    
    # Create DataFrame
    df = pd.DataFrame(all_repos)
    
    # Remove duplicates
    df = df.drop_duplicates(subset=["full_name"])
    
    logger.info(f"Total unique repositories: {len(df)}")
    
    # Save raw data
    data_manager = DataManager()
    data_manager.save_json(all_repos, f"trending_repos_{get_timestamp().replace(' ', '_').replace(':', '-')}.json")
    
    return df
