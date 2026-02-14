import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import requests

class FeatureExtractor:
    def __init__(self, url: str, html_content: str = None):
        self.url = url
        
        # If no HTML sent, try to fetch it from the internet
        if not html_content:
            try:
                response = requests.get(url, timeout=3)
                self.html = response.text
            except:
                self.html = "" # Fallback if site is offline
        else:
            self.html = html_content
            
        self.soup = BeautifulSoup(self.html, 'html.parser')
        self.domain = urlparse(url).netloc

    def extract(self):
        # ... (Keep the rest of the extract function and feature methods exactly as they were) ...
        # (Just ensure the methods below 'def extract(self):' are still there!)
        features = []
        features.append(self.has_ip_address())
        features.append(self.url_length())
        features.append(self.is_tiny_url())
        features.append(self.has_at_symbol())
        features.append(self.iframe_count())
        features.append(self.mouse_over_status())
        features.append(self.right_click_disabled())
        features.append(self.form_action_invalid())
        features.append(self.password_field_count())
        return features

    # ... (Keep all your helper functions: has_ip_address, url_length, etc.) ...
    # ...

    # --- Feature Logic ---

    def has_ip_address(self):
        # Checks if domain is an IP address (e.g., http://192.168.1.1)
        ip_pattern = r'(([01]?\d\d?|2[0-4]\d|25[0-5])\.([01]?\d\d?|2[0-4]\d|25[0-5])\.([01]?\d\d?|2[0-4]\d|25[0-5])\.([01]?\d\d?|2[0-4]\d|25[0-5])\/)|' 
        match = re.search(ip_pattern, self.url)
        return 1 if match else 0

    def url_length(self):
        # Phishing URLs are often very long
        return 1 if len(self.url) > 75 else 0

    def is_tiny_url(self):
        # Checks for shortening services
        shorteners = r"bit\.ly|goo\.gl|shorte\.st|go2l\.ink|x\.co|ow\.ly|t\.co|tinyurl|tr\.im|is\.gd|cli\.gs"
        match = re.search(shorteners, self.url)
        return 1 if match else 0

    def has_at_symbol(self):
        # @ symbol ignores everything before it in browsers
        return 1 if "@" in self.url else 0

    def iframe_count(self):
        # Phishers use iframes to hide content
        iframes = self.soup.find_all('iframe')
        return 1 if len(iframes) > 0 else 0

    def mouse_over_status(self):
        # Look for status bar spoofing in JS
        if re.findall("<script>.+onmouseover.+</script>", self.html):
            return 1
        return 0

    def right_click_disabled(self):
        # Phishers often disable right-click to hide source code
        if re.findall(r"event.button ?== ?2", self.html):
            return 1
        return 0
        
    def form_action_invalid(self):
        # Checks if form sends data to a different domain or is empty
        forms = self.soup.find_all('form')
        for form in forms:
            action = form.get('action')
            if not action or action == "" or action == "about:blank":
                return 1
            if self.domain not in action and "http" in action:
                return 1 # Sending data to foreign domain
        return 0
        
    def password_field_count(self):
        # Phishing sites usually ask for passwords
        inputs = self.soup.find_all('input', {'type': 'password'})
        return len(inputs)