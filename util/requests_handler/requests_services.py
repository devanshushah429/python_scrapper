import requests
class RequestsServices:
    def __init__(self, url):
        self.url = url
    
    def get_page_source_by_url_using_requests(self):
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        response = requests.get(self.url, headers=headers)
        if response.status_code == 200:
            return response.text
        else:
            print(f'Failed to retrieve the page. Status code: {response.status_code}')
            print(response)
            return None
