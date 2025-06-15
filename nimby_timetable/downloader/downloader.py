import requests

class WebDownloader:
    def download(self, url) -> str:
        if url.startswith("file"):
            filepath = url.split("Debian")[1]
            with open(filepath) as f:
                body = f.read()
        else:
            response = requests.get(url)
            response.raise_for_status()
            body = response.text
        
        return body

