import requests
import json
from datetime import datetime, timedelta
from utilities import log_output

class NewsHandler:
    def __init__(self):
        self.api_key = "30d454670a7b442f9871e4db8815a171"  # Replace with your NewsAPI key
        self.headlines_url = "https://newsapi.org/v2/top-headlines"
        self.everything_url = "https://newsapi.org/v2/everything"
        self.country_codes = self.load_country_codes()

    def load_country_codes(self):
        try:
            with open('country_codes.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            log_output(None, "Error: country_codes.json not found")
            return {}
        except json.JSONDecodeError:
            log_output(None, "Error: Invalid JSON in country_codes.json")
            return {}

    def fetch_news(self, country=None, category=None, text_area=None):
        """
        Fetch news based on country and/or category using appropriate endpoint
        """
        debug_info = ["Debug Information:"]

        # Use top-headlines for category-only searches
        if category and not country:
            return self.fetch_headlines(category=category, debug_info=debug_info)
        
        # Use everything endpoint with query for country searches
        from_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        params = {
            'apiKey': self.api_key,
            'pageSize': 5,
            'language': 'en',
            'sortBy': 'publishedAt',
            'from': from_date
        }

        # Build the query
        if country:
            # Use the country name in the query
            params['q'] = f'"{country}" news'
            if category:
                params['q'] += f' AND {category}'
        else:
            params['q'] = 'world news'
            if category:
                params['q'] += f' AND {category}'

        debug_info.append(f"Request URL: {self.everything_url}")
        debug_info.append(f"Parameters (excluding API key): {str({k:v for k,v in params.items() if k != 'apiKey'})}")

        try:
            response = requests.get(self.everything_url, params=params)
            debug_info.append(f"Response Status Code: {response.status_code}")
            debug_info.append(f"Response Headers: {dict(response.headers)}")
            
            if response.content:
                news_data = response.json()
                debug_info.append(f"Response Status: {news_data.get('status')}")
                debug_info.append(f"Total Results: {news_data.get('totalResults', 0)}")
                
                if news_data.get('status') == 'error':
                    debug_info.append(f"API Error: {news_data.get('message', 'Unknown error')}")
                    return f"API Error: {news_data.get('message', 'Unknown error')}\n\n" + "\n".join(debug_info)
                
                if news_data.get('status') == 'ok':
                    articles = news_data.get('articles', [])
                    if articles:
                        return self.format_news(articles, country, category)
                    else:
                        debug_info.append("No articles found in the response")
                        return "No news articles found. Try broadening your search or using different keywords.\n\n" + "\n".join(debug_info)
            
            return "Error: Empty response from News API\n\n" + "\n".join(debug_info)
                
        except requests.exceptions.RequestException as e:
            debug_info.append(f"Request Exception: {str(e)}")
            return f"Error fetching news: {str(e)}\n\n" + "\n".join(debug_info)
        except Exception as e:
            debug_info.append(f"Unexpected Error: {str(e)}")
            return f"Unexpected error: {str(e)}\n\n" + "\n".join(debug_info)

    def fetch_headlines(self, category=None, debug_info=None):
        """
        Fetch headlines using the top-headlines endpoint
        """
        if debug_info is None:
            debug_info = ["Debug Information:"]

        params = {
            'apiKey': self.api_key,
            'pageSize': 5,
            'language': 'en'
        }

        if category:
            params['category'] = category.lower()

        debug_info.append(f"Request URL: {self.headlines_url}")
        debug_info.append(f"Parameters (excluding API key): {str({k:v for k,v in params.items() if k != 'apiKey'})}")

        try:
            response = requests.get(self.headlines_url, params=params)
            debug_info.append(f"Response Status Code: {response.status_code}")
            
            if response.content:
                news_data = response.json()
                if news_data.get('status') == 'ok':
                    articles = news_data.get('articles', [])
                    if articles:
                        return self.format_news(articles, category=category)
                    
            return "No headlines found\n\n" + "\n".join(debug_info)
            
        except Exception as e:
            return f"Error fetching headlines: {str(e)}\n\n" + "\n".join(debug_info)

    def format_news(self, articles, country=None, category=None):
        """Format the news articles for display"""
        if not articles:
            return "No news articles found."
            
        header = "=== Latest News ==="
        if country:
            header += f" for {country.title()}"
        if category:
            header += f" - {category.title()} category"
        
        formatted_news = f"\n{header}\n\n"
        
        for i, article in enumerate(articles, 1):
            pub_date = datetime.strptime(article['publishedAt'], '%Y-%m-%dT%H:%M:%SZ').strftime('%Y-%m-%d %H:%M')
            formatted_news += f"{i}. {article['title']}\n\n"
            formatted_news += f"   Source: {article['source']['name']}\n"
            formatted_news += f"   Published: {pub_date}\n"
            if article.get('description'):
                formatted_news += f"   \nDescription: {article['description']}\n\n"
            formatted_news += f"   URL: {article['url']}\n\n"
            
        return formatted_news

    def validate_category(self, category):
        valid_categories = ['business', 'entertainment', 'general', 'health', 
                          'science', 'sports', 'technology']
        return category.lower() in valid_categories

    def get_country_code(self, country_name):
        country_name = country_name.lower().strip()
        return self.country_codes.get(country_name)

    def get_available_countries(self):
        """Return list of available countries"""
        return "\nAvailable Countries:\n" + "\n".join(sorted(self.country_codes.keys()))

    def get_available_categories(self):
        """Return list of available categories"""
        categories = ['business', 'entertainment', 'general', 'health', 
                     'science', 'sports', 'technology']
        return "\nAvailable Categories:\n" + "\n".join(categories)

def handle_news_command(command_args, text_area):
    news_handler = NewsHandler()
    
    if not command_args:
        # General news
        result = news_handler.fetch_headlines(text_area=text_area)
        log_output(text_area, result)
        return

    cmd_type = command_args[0].lower()
    
    if cmd_type == "countries":
        result = news_handler.get_available_countries()
    
    elif cmd_type == "categories":
        result = news_handler.get_available_categories()
    
    elif cmd_type == "category" and len(command_args) > 1:
        category = command_args[1].lower()
        result = news_handler.fetch_headlines(category=category)
        
    elif cmd_type == "country" and len(command_args) > 1:
        country = " ".join(command_args[1:])
        result = news_handler.fetch_news(country=country)
        
    elif cmd_type == "country-category" and len(command_args) > 2:
        country = " ".join(command_args[1:-1])
        category = command_args[-1].lower()
        result = news_handler.fetch_news(country=country, category=category)
        
    else:
        result = """
Usage:
- news : Get general top news
- news countries : List all available countries
- news categories : List all available categories
- news category <category> : Get news by category
- news country <country_name> : Get news by country
- news country-category <country_name> <category> : Get news by country and category

Example:
- news country united states
- news category technology
- news country-category united kingdom sports
"""
    
    log_output(text_area, result)