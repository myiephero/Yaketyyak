"""
GitHub Repository Analyzer
Fetches repo metadata and provides plain-English analysis
"""

import re
import httpx
from typing import Optional, Dict
from datetime import datetime, timezone


def parse_github_url(url: str) -> Optional[Dict[str, str]]:
    """
    Parse a GitHub URL to extract owner and repo name.
    Supports various GitHub URL formats.
    """
    patterns = [
        r"github\.com/([^/]+)/([^/\s?#]+)",  # Standard URL
        r"github\.com:([^/]+)/([^/\s.]+)",    # SSH format
        r"^([^/]+)/([^/\s]+)$",                # owner/repo format
    ]
    
    url = url.strip().rstrip("/").replace(".git", "")
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return {
                "owner": match.group(1),
                "repo": match.group(2)
            }
    
    return None


def format_number(num: int) -> str:
    """Format large numbers for display (e.g., 1500 -> 1.5k)"""
    if num >= 1000000:
        return f"{num / 1000000:.1f}M"
    elif num >= 1000:
        return f"{num / 1000:.1f}k"
    return str(num)


def get_quality_assessment(data: Dict) -> Dict:
    """
    Analyze repo metrics and provide a quality assessment.
    """
    stars = data.get("stargazers_count", 0)
    forks = data.get("forks_count", 0)
    issues = data.get("open_issues_count", 0)
    
    # Calculate a simple quality score
    score = 0
    reasons = []
    warnings = []
    
    # Stars assessment
    if stars >= 10000:
        score += 30
        reasons.append("Highly popular with 10k+ stars")
    elif stars >= 1000:
        score += 25
        reasons.append("Well-established with 1k+ stars")
    elif stars >= 100:
        score += 15
        reasons.append("Gaining traction with 100+ stars")
    elif stars >= 10:
        score += 5
        reasons.append("Small but active community")
    else:
        warnings.append("Very few stars - may be new or unmaintained")
    
    # Forks assessment
    if forks >= 1000:
        score += 20
        reasons.append("Widely forked - active developer community")
    elif forks >= 100:
        score += 15
        reasons.append("Good fork activity")
    elif forks >= 10:
        score += 5
    
    # Issues assessment
    if issues > 100:
        warnings.append(f"High number of open issues ({issues}) - may need attention")
    elif issues > 0:
        reasons.append("Active issue tracking")
    
    # License check
    license_info = data.get("license")
    if license_info:
        score += 10
        reasons.append(f"Open source licensed ({license_info.get('spdx_id', 'Unknown')})")
    else:
        warnings.append("No license specified - usage rights unclear")
    
    # Activity check
    updated_at = data.get("updated_at")
    if updated_at:
        try:
            last_update = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
            days_since_update = (datetime.now(timezone.utc) - last_update).days
            
            if days_since_update <= 30:
                score += 15
                reasons.append("Recently updated (within 30 days)")
            elif days_since_update <= 90:
                score += 10
                reasons.append("Updated within last 3 months")
            elif days_since_update > 365:
                warnings.append(f"Not updated in {days_since_update} days - may be abandoned")
        except (ValueError, TypeError):
            pass
    
    # Determine quality tier
    if score >= 60:
        tier = "excellent"
        tier_label = "Excellent"
        tier_color = "#10b981"  # Green
    elif score >= 40:
        tier = "good"
        tier_label = "Good"
        tier_color = "#8b5cf6"  # Purple
    elif score >= 20:
        tier = "fair"
        tier_label = "Fair"
        tier_color = "#f59e0b"  # Amber
    else:
        tier = "caution"
        tier_label = "Use Caution"
        tier_color = "#f43f5e"  # Red
    
    return {
        "score": min(score, 100),
        "tier": tier,
        "tier_label": tier_label,
        "tier_color": tier_color,
        "reasons": reasons,
        "warnings": warnings
    }


def generate_summary(data: Dict, mode: str = "beginner") -> str:
    """Generate a plain-English summary of the repository."""
    name = data.get("name", "Unknown")
    description = data.get("description", "No description provided")
    language = data.get("language", "Unknown")
    stars = data.get("stargazers_count", 0)
    forks = data.get("forks_count", 0)
    issues = data.get("open_issues_count", 0)
    topics = data.get("topics", [])
    
    assessment = get_quality_assessment(data)
    
    if mode == "beginner":
        summary = f"""## What is {name}?

{description}

### In Plain English:
This is a **{language or 'multi-language'}** project that has been "starred" (liked/bookmarked) by **{format_number(stars)}** developers - """
        
        if stars >= 10000:
            summary += "that's a LOT, meaning this is a very popular and trusted project!"
        elif stars >= 1000:
            summary += "that's quite a lot, showing this is a well-established project."
        elif stars >= 100:
            summary += "a decent amount, showing growing community interest."
        else:
            summary += "it's still growing its community."
        
        summary += f"""

### Should You Use It?
**Quality Assessment: {assessment['tier_label']}** (Score: {assessment['score']}/100)

✅ **Good Signs:**
"""
        for reason in assessment['reasons'][:4]:
            summary += f"- {reason}\n"
        
        if assessment['warnings']:
            summary += "\n⚠️ **Things to Consider:**\n"
            for warning in assessment['warnings'][:3]:
                summary += f"- {warning}\n"
        
        if topics:
            summary += f"\n### Related Topics:\n{', '.join(topics[:8])}"
            
    else:  # familiar mode
        summary = f"""**{name}**: {description}

**Stack:** {language or 'Multi-language'} | ⭐ {format_number(stars)} | 🍴 {format_number(forks)} | 📋 {issues} issues

**Assessment: {assessment['tier_label']}** ({assessment['score']}/100)
- {' | '.join(assessment['reasons'][:3])}"""
        
        if assessment['warnings']:
            summary += f"\n⚠️ {assessment['warnings'][0]}"
    
    return summary


async def analyze_repo(url: str, mode: str = "beginner") -> Dict:
    """
    Fetch and analyze a GitHub repository.
    
    Args:
        url: GitHub repository URL
        mode: "beginner" or "familiar"
    
    Returns:
        Dict with repo data and analysis
    """
    parsed = parse_github_url(url)
    
    if not parsed:
        return {
            "error": True,
            "message": "Invalid GitHub URL. Please use a format like: https://github.com/owner/repo"
        }
    
    owner = parsed["owner"]
    repo = parsed["repo"]
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Fetch main repo data
            response = await client.get(
                f"https://api.github.com/repos/{owner}/{repo}",
                headers={"Accept": "application/vnd.github.v3+json"}
            )
            
            if response.status_code == 404:
                return {
                    "error": True,
                    "message": f"Repository '{owner}/{repo}' not found. Check if the URL is correct and the repo is public."
                }
            elif response.status_code == 403:
                return {
                    "error": True,
                    "message": "GitHub API rate limit exceeded. Please try again in a few minutes."
                }
            elif response.status_code != 200:
                return {
                    "error": True,
                    "message": f"GitHub API error: {response.status_code}"
                }
            
            data = response.json()
            
            # Fetch additional data
            contributors_count = 0
            try:
                contrib_response = await client.get(
                    f"https://api.github.com/repos/{owner}/{repo}/contributors?per_page=1",
                    headers={"Accept": "application/vnd.github.v3+json"}
                )
                if contrib_response.status_code == 200:
                    # Get count from Link header
                    link_header = contrib_response.headers.get("Link", "")
                    if 'rel="last"' in link_header:
                        match = re.search(r'page=(\d+)>; rel="last"', link_header)
                        if match:
                            contributors_count = int(match.group(1))
                    else:
                        contributors_count = len(contrib_response.json())
            except (httpx.HTTPError, ValueError, KeyError):
                pass
            
            # Get latest release if exists
            latest_release = None
            try:
                release_response = await client.get(
                    f"https://api.github.com/repos/{owner}/{repo}/releases/latest",
                    headers={"Accept": "application/vnd.github.v3+json"}
                )
                if release_response.status_code == 200:
                    release_data = release_response.json()
                    latest_release = {
                        "tag": release_data.get("tag_name"),
                        "name": release_data.get("name"),
                        "published_at": release_data.get("published_at")
                    }
            except (httpx.HTTPError, ValueError, KeyError):
                pass
            
            # Build response
            assessment = get_quality_assessment(data)
            
            return {
                "error": False,
                "repo": {
                    "name": data.get("name"),
                    "full_name": data.get("full_name"),
                    "description": data.get("description"),
                    "url": data.get("html_url"),
                    "homepage": data.get("homepage"),
                    "language": data.get("language"),
                    "topics": data.get("topics", []),
                    "default_branch": data.get("default_branch"),
                    "created_at": data.get("created_at"),
                    "updated_at": data.get("updated_at"),
                    "pushed_at": data.get("pushed_at"),
                },
                "stats": {
                    "stars": data.get("stargazers_count", 0),
                    "stars_formatted": format_number(data.get("stargazers_count", 0)),
                    "forks": data.get("forks_count", 0),
                    "forks_formatted": format_number(data.get("forks_count", 0)),
                    "watchers": data.get("watchers_count", 0),
                    "watchers_formatted": format_number(data.get("watchers_count", 0)),
                    "open_issues": data.get("open_issues_count", 0),
                    "size_kb": data.get("size", 0),
                    "contributors": contributors_count,
                    "contributors_formatted": format_number(contributors_count) if contributors_count else "N/A",
                },
                "meta": {
                    "license": data.get("license", {}).get("spdx_id") if data.get("license") else None,
                    "license_name": data.get("license", {}).get("name") if data.get("license") else "No License",
                    "is_fork": data.get("fork", False),
                    "is_archived": data.get("archived", False),
                    "is_template": data.get("is_template", False),
                    "has_wiki": data.get("has_wiki", False),
                    "has_pages": data.get("has_pages", False),
                    "has_discussions": data.get("has_discussions", False),
                    "latest_release": latest_release,
                },
                "owner": {
                    "login": data.get("owner", {}).get("login"),
                    "avatar_url": data.get("owner", {}).get("avatar_url"),
                    "type": data.get("owner", {}).get("type"),
                },
                "assessment": assessment,
                "summary": generate_summary(data, mode)
            }
            
    except httpx.TimeoutException:
        return {
            "error": True,
            "message": "Request timed out. GitHub may be slow or unavailable."
        }
    except Exception as e:
        return {
            "error": True,
            "message": f"An error occurred: {str(e)}"
        }
