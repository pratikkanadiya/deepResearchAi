import ipaddress
from io import BytesIO
import socket
from urllib.parse import urljoin, urlparse

import requests

from bs4 import BeautifulSoup


class DocumentReaderTool:

    MAX_REDIRECTS = 5
    MAX_BYTES = 5_000_000
    MAX_PDF_PAGES = 100

    def __init__(self):

        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "Chrome/153.0 Safari/537.36"
            )
        }

    def read(
        self,
        url: str,
        max_chars: int = 20000
    ) -> dict:

        current_url = url
        response = None

        for _ in range(self.MAX_REDIRECTS + 1):
            self._validate_public_url(current_url)
            response = requests.get(
                current_url,
                headers=self.headers,
                timeout=(5, 20),
                allow_redirects=False,
                stream=True,
            )
            if response.is_redirect or response.is_permanent_redirect:
                location = response.headers.get("Location")
                response.close()
                if not location:
                    raise ValueError("Redirect response did not include a Location header.")
                current_url = urljoin(current_url, location)
                continue
            response.raise_for_status()
            break
        else:
            raise ValueError("Too many redirects while reading source.")

        content_type = response.headers.get("Content-Type", "").split(";", 1)[0].strip().lower()

        content_length = response.headers.get("Content-Length")
        if content_length and int(content_length) > self.MAX_BYTES:
            response.close()
            raise ValueError("Source document exceeds the maximum download size.")

        body = bytearray()
        for chunk in response.iter_content(chunk_size=65536):
            body.extend(chunk)
            if len(body) > self.MAX_BYTES:
                response.close()
                raise ValueError("Source document exceeds the maximum download size.")
        response.close()

        status_code = response.status_code

        is_pdf = content_type == "application/pdf" or bytes(body[:5]) == b"%PDF-"
        if is_pdf:
            title, text = self._extract_pdf(bytes(body))
            return {
                "url": current_url,
                "title": title or self._title_from_url(current_url),
                "content": text[:max_chars],
                "content_length": len(text),
                "status_code": status_code,
            }

        if content_type not in {"text/html", "application/xhtml+xml"}:
            raise ValueError(f"Unsupported document content type: {content_type or 'unknown'}")

        encoding = response.encoding or "utf-8"
        html = bytes(body).decode(encoding, errors="replace")

        soup = BeautifulSoup(
            html,
            "html.parser"
        )

        for element in soup([
            "script",
            "style",
            "nav",
            "footer",
            "header",
            "aside"
        ]):
            element.decompose()

        text = soup.get_text(
            separator=" ",
            strip=True
        )

        return {
            "url": current_url,
            "title": (
                soup.title.get_text(strip=True)
                if soup.title
                else ""
            ),
            "content": text[:max_chars],
            "content_length": len(text),
            "status_code": status_code
        }

    @classmethod
    def _extract_pdf(cls, data: bytes) -> tuple[str, str]:
        try:
            from pypdf import PdfReader

            reader = PdfReader(BytesIO(data))
            text = "\n".join(
                page.extract_text() or ""
                for page in reader.pages[: cls.MAX_PDF_PAGES]
            ).strip()
            if not text:
                raise ValueError("PDF contains no extractable text (it may be scanned).")
            metadata = reader.metadata
            title = str(metadata.title).strip() if metadata and metadata.title else ""
            return title, text
        except ValueError:
            raise
        except Exception as exc:
            raise ValueError(f"Could not extract text from PDF: {exc}") from exc

    @staticmethod
    def _title_from_url(url: str) -> str:
        return urlparse(url).path.rstrip("/").rsplit("/", 1)[-1] or urlparse(url).netloc

    @staticmethod
    def _validate_public_url(url: str) -> None:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            raise ValueError("Only public HTTP and HTTPS URLs are allowed.")
        if parsed.username or parsed.password:
            raise ValueError("URLs containing credentials are not allowed.")

        hostname = parsed.hostname.rstrip(".").lower()
        if hostname == "localhost" or hostname.endswith(".localhost") or hostname.endswith(".local"):
            raise ValueError("Local network URLs are not allowed.")

        try:
            addresses = {ipaddress.ip_address(hostname)}
        except ValueError:
            try:
                addresses = {
                    ipaddress.ip_address(record[4][0])
                    for record in socket.getaddrinfo(hostname, parsed.port or 443 if parsed.scheme == "https" else parsed.port or 80)
                }
            except OSError as exc:
                raise ValueError("Could not resolve source host.") from exc

        if not addresses or any(not address.is_global for address in addresses):
            raise ValueError("Local or non-public network addresses are not allowed.")


if __name__ == "__main__":

    reader = DocumentReaderTool()

    result = reader.read(
        "https://example.com"
    )

    print("TITLE:")
    print(result["title"])

    print("\nURL:")
    print(result["url"])

    print("\nCONTENT:")
    print(result["content"][:2000])
