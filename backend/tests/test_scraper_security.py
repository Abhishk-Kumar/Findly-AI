import pytest
from backend.app.services.scraper_service import ScraperService


def test_ssrf_blocks_private_ips():
    # Loopback
    is_safe, reason = ScraperService.is_safe_url("http://127.0.0.1:8080/admin")
    assert is_safe is False
    assert "Prohibited IP" in reason or "localhost" in reason

    # Localhost hostname
    is_safe, reason = ScraperService.is_safe_url("http://localhost:3000/secret")
    assert is_safe is False
    assert "localhost" in reason

    # AWS metadata IP
    is_safe, reason = ScraperService.is_safe_url("http://169.254.169.254/latest/meta-data/")
    assert is_safe is False
    assert "Prohibited IP" in reason

    # Private Class A network
    is_safe, reason = ScraperService.is_safe_url("http://10.0.0.5/internal")
    assert is_safe is False
    assert "Prohibited IP" in reason


def test_scheme_validation():
    # Disallow file scheme
    is_safe, reason = ScraperService.is_safe_url("file:///etc/passwd")
    assert is_safe is False
    assert "Invalid scheme" in reason

    # Disallow ftp scheme
    is_safe, reason = ScraperService.is_safe_url("ftp://ftp.example.com/file.txt")
    assert is_safe is False
    assert "Invalid scheme" in reason


def test_clean_html_text_extraction():
    html_sample = """
    <html>
      <head><title>Test Article</title></head>
      <body>
        <nav><a href="/">Home</a><a href="/about">About</a></nav>
        <script>console.log("malicious or noise script");</script>
        <style>body { color: red; }</style>
        <main>
          <h1>Breakthrough in Quantum Computing</h1>
          <p>Researchers have demonstrated high-fidelity quantum error correction using surface codes.</p>
        </main>
        <footer>Copyright 2026</footer>
      </body>
    </html>
    """
    clean = ScraperService.extract_clean_text(html_sample)
    assert "Breakthrough in Quantum Computing" in clean
    assert "surface codes" in clean
    assert "console.log" not in clean
    assert "color: red" not in clean
    assert "Copyright" not in clean


def test_scrape_url_graceful_failure_on_invalid_host():
    result = ScraperService.scrape_url("https://this-domain-does-not-exist-12345xyz987.org/test")
    assert result["status"] == "failed"
    assert result["text"] is None
    assert result["error"] is not None
