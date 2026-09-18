from typing import List, Dict, Any, Optional
from urllib.parse import urlparse
from tavily import TavilyClient
from backend.app.config import get_settings


class TavilyService:
    def __init__(self, api_key: Optional[str] = None):
        settings = get_settings()
        self.api_key = api_key or settings.TAVILY_API_KEY
        self.client = None
        if self.api_key and self.api_key.strip():
            self.client = TavilyClient(api_key=self.api_key.strip())

    def is_configured(self) -> bool:
        return bool(self.client)

    def search(
        self,
        query: str,
        max_results: int = 6,
        search_depth: str = "advanced",
    ) -> List[Dict[str, Any]]:
        if not self.client:
            raise RuntimeError(
                "TAVILY_API_KEY is missing or empty. Please set TAVILY_API_KEY in your .env file "
                "or environment variables."
            )

        try:
            response = self.client.search(
                query=query,
                search_depth=search_depth,
                max_results=max_results,
            )
            raw_results = response.get("results", [])

            deduped_sources = {}
            for item in raw_results:
                url = item.get("url", "").strip()
                if not url or url in deduped_sources:
                    continue

                parsed = urlparse(url)
                domain = parsed.netloc or ""
                title = item.get("title", "").strip() or domain or "Untitled Source"
                snippet = item.get("content", "").strip()
                score = float(item.get("score", 0.0))

                deduped_sources[url] = {
                    "url": url,
                    "title": title,
                    "domain": domain,
                    "snippet": snippet,
                    "relevance_score": score,
                    "status": "discovered",
                }

            return list(deduped_sources.values())

        except Exception as e:
            msg = str(e).lower()
            if "unauthorized" in msg or "key" in msg or "401" in msg or "forbidden" in msg:
                raise RuntimeError("Tavily authentication failed. Check your TAVILY_API_KEY.") from e
            raise RuntimeError(f"Tavily search failed: {str(e)}") from e
