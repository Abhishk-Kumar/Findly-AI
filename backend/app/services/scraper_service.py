import ipaddress
import re
import socket
from typing import Dict, Any, Optional
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup


class ScraperService:
    # Reserved and private network ranges for SSRF prevention
    BLOCKED_IP_NETWORKS = [
        ipaddress.ip_network("0.0.0.0/8"),
        ipaddress.ip_network("10.0.0.0/8"),
        ipaddress.ip_network("100.64.0.0/10"),
        ipaddress.ip_network("127.0.0.0/8"),
        ipaddress.ip_network("169.254.0.0/16"),
        ipaddress.ip_network("172.16.0.0/12"),
        ipaddress.ip_network("192.0.0.0/24"),
        ipaddress.ip_network("192.0.2.0/24"),
        ipaddress.ip_network("192.168.0.0/16"),
        ipaddress.ip_network("198.18.0.0/15"),
        ipaddress.ip_network("198.51.100.0/24"),
        ipaddress.ip_network("203.0.113.0/24"),
        ipaddress.ip_network("224.0.0.0/4"),
        ipaddress.ip_network("240.0.0.0/4"),
        ipaddress.ip_network("255.255.255.255/32"),
        # IPv6
        ipaddress.ip_network("::1/128"),
        ipaddress.ip_network("fc00::/7"),
        ipaddress.ip_network("fe80::/10"),
    ]

    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 FindlyResearchBot/2.0"

    @classmethod
    def is_safe_url(cls, url: str) -> tuple[bool, Optional[str]]:
        try:
            parsed = urlparse(url)
            if parsed.scheme not in ("http", "https"):
                return False, f"Invalid scheme: {parsed.scheme}. Only HTTP/HTTPS supported."

            hostname = parsed.hostname
            if not hostname:
                return False, "Missing hostname."

            # Disallow localhost directly
            if hostname.lower() in ("localhost", "127.0.0.1", "::1", "0.0.0.0"):
                return False, "Access to localhost is prohibited."

            # Resolve DNS to check IP for SSRF
            try:
                addr_info = socket.getaddrinfo(hostname, None)
                for addr in addr_info:
                    ip_str = addr[4][0]
                    ip = ipaddress.ip_address(ip_str)
                    for network in cls.BLOCKED_IP_NETWORKS:
                        if ip in network:
                            return False, f"Prohibited IP address range ({ip_str})"
            except (socket.gaierror, ValueError):
                return False, f"Could not resolve hostname: {hostname}"

            return True, None
        except Exception as e:
            return False, f"URL validation error: {str(e)}"

    @classmethod
    def extract_clean_text(cls, html_content: str) -> str:
        soup = BeautifulSoup(html_content, "html.parser")

        # Decompose unwanted noise tags
        for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form", "svg", "noscript"]):
            tag.decompose()

        # Extract main text
        text = " ".join(soup.stripped_strings)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    @classmethod
    def scrape_url(cls, url: str, timeout: int = 10, max_chars: int = 5000) -> Dict[str, Any]:
        parsed = urlparse(url)
        domain = parsed.netloc or ""

        # Validate security / SSRF
        is_safe, reason = cls.is_safe_url(url)
        if not is_safe:
            return {
                "url": url,
                "domain": domain,
                "title": domain or "Blocked URL",
                "text": None,
                "status": "failed",
                "error": f"Security restriction: {reason}",
                "char_count": 0,
            }

        headers = {
            "User-Agent": cls.USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }

        try:
            resp = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
            resp.raise_for_status()

            # Ensure response is text/html
            content_type = resp.headers.get("Content-Type", "").lower()
            if "text/html" not in content_type and "application/xhtml" not in content_type and "text/plain" not in content_type:
                return {
                    "url": url,
                    "domain": domain,
                    "title": domain,
                    "text": None,
                    "status": "skipped",
                    "error": f"Unsupported content type: {content_type}",
                    "char_count": 0,
                }

            soup = BeautifulSoup(resp.text, "html.parser")
            title = soup.title.string.strip() if soup.title and soup.title.string else domain

            clean_text = cls.extract_clean_text(resp.text)
            if not clean_text or len(clean_text) < 50:
                return {
                    "url": url,
                    "domain": domain,
                    "title": title,
                    "text": None,
                    "status": "failed",
                    "error": "Extracted text too short or empty",
                    "char_count": 0,
                }

            truncated = clean_text[:max_chars]
            return {
                "url": url,
                "domain": domain,
                "title": title,
                "text": truncated,
                "status": "scraped",
                "error": None,
                "char_count": len(truncated),
            }

        except requests.exceptions.Timeout:
            return {
                "url": url,
                "domain": domain,
                "title": domain,
                "text": None,
                "status": "failed",
                "error": f"Request timed out after {timeout} seconds",
                "char_count": 0,
            }
        except requests.exceptions.RequestException as e:
            return {
                "url": url,
                "domain": domain,
                "title": domain,
                "text": None,
                "status": "failed",
                "error": f"HTTP error: {str(e)}",
                "char_count": 0,
            }
        except Exception as e:
            return {
                "url": url,
                "domain": domain,
                "title": domain,
                "text": None,
                "status": "failed",
                "error": f"Scraping error: {str(e)}",
                "char_count": 0,
            }
