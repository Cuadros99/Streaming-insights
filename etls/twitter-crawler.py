import os
import json
from dotenv import load_dotenv
from datetime import datetime
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Load environment variables from the parent directory's .env file
load_dotenv('/../.env')


class TwitterCrawler:
    def __init__(self):

        # Create a relative path to the etls directory
        self.ETLS_DIR = os.path.dirname(__file__)

        # Define Selenium paramaters
        self.options = Options()
        self.options.add_argument('--disable-dev-shm-usage')

        # Import a list with the main streaming platforms
        file_path = os.path.join(self.ETLS_DIR ,'streaming_platforms.json')
        with open(file_path, 'r') as json_file:
            self.streaming_platforms = json.load(json_file)

        # Keywords
        self.keywords = ["bom", "ruim", "chato", "legal", "amo", "odeio", "muito", "pouco", "maratona", "maratonando", "assistir", "assistindo", "vsf", "lol", "mds", "foda", "merda", "tnc", "site", "aplicativo", "player", "lixo", "pqp", "app", "curtindo", "curti", "otimo", "maravilhoso", "maravilhosa", "horrivel", "bosta", "coco", "melhor","pior", "adoro", "caro", "cara","barato"]
        # Define the common filters
        self.common_filters = "-filter:links -filter:replies"
        # Define the period (since:2023-08-01)
        self.period = f"since:{datetime.now().date()}"
        # Define the language (lang:pt)
        self.language = "lang:pt"
        
        # Define the html list of pages
        self.html_source_dict = {}
        for platform in self.streaming_platforms:
            self.html_source_dict[platform] = []

    # Create advanced search queries for each streaming platform
    def create_advanced_search(self):
        self.advanced_queries = {}
        for platform in self.streaming_platforms:
            # Construct the query for mentioned accounts
            keywords_query = " OR ".join(self.keywords)

            # Combine all components to create the advanced search query
            search_query = f'{platform} ({keywords_query}) {self.language} {self.period} {self.common_filters}'

            # Add the query to the advances queries list
            self.advanced_queries[platform] = search_query

    def login_twitter(self, platform):
        platform_dash_name = platform.upper().replace(' ', '_')
        try:
            self.insert_text(os.getenv(f'TWITTER_LOGIN_{platform_dash_name}'), '//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[5]/label/div/div[2]/div/input' )
            self.insert_text(os.getenv(f'TWITTER_USERNAME_{platform_dash_name}'), '//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div[2]/label/div/div[2]/div/input')
            self.insert_text(os.getenv('TWITTER_PASS'), '//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div/div[3]/div/label/div/div[2]/div[1]/input',40)
        except Exception as e:
            print("An unexpected error occurred:", e)

    def insert_text(self, text, XPATH, timeout = 30):
        input_text = self.wait_for_element(XPATH, timeout=timeout)
        if input_text:
            input_text.send_keys(text)
            input_text.send_keys(Keys.RETURN)

    def wait_for_element(self, locator, by_type = By.XPATH, timeout=30):
        element = WebDriverWait(self.driver, timeout).until( EC.presence_of_element_located((by_type,locator)))
        return element

    def make_search(self, platform, adv_search):
        try:
            # Enter in the Explore Tab
            self.wait_for_element('//*[@id="react-root"]/div/div/div[2]/header/div/div/div/div[1]/div[2]/nav/a[2]/div').click()
            # Insert text in the search bar 
            self.insert_text(adv_search, '//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div[1]/div[1]/div[1]/div/div/div/div/div[1]/div[2]/div/div/div/form/div[1]/div/div/div/label/div[2]/div/input',90)
            # Enter in the Latest Tab
            self.wait_for_element('//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div[1]/div[1]/div[2]/nav/div/div[2]/div/div[2]/a').click()
            # Scroll down to load more tweets
            self.scroll_down(platform)
    
        except Exception as e:
            print("An unexpected error occurred:", e)
        
    def scroll_down(self, platform, target_tweets_count = 400, scroll_pause_time = 3):
        # Waits until the first tweet appears
        self.wait_for_element('div[data-testid="cellInnerDiv"]', By.CSS_SELECTOR)
        # Count the number of tweets on the page
        tweets_count = len(self.driver.find_elements(By.CSS_SELECTOR, 'div[data-testid="cellInnerDiv"]'))
        # Get scroll height
        last_height = self.driver.execute_script("return document.body.scrollHeight")

        # Scroll down through the screen
        while tweets_count < target_tweets_count:
            # Get the html page
            self.get_html(platform)
            # Scroll down to bottom
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # Wait to load page
            time.sleep(scroll_pause_time)

            # Update the counter of tweets
            tweets_count += len(self.driver.find_elements(By.CSS_SELECTOR, 'div[data-testid="cellInnerDiv"]'))
            print(tweets_count)

            # Calculate new scroll height and compare with last scroll height
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
    
    def get_html(self, platform):
        html = self.driver.page_source
        self.html_source_dict[platform].append(html)
        
    def export_html_pages(self):
        for platform in self.streaming_platforms:
            platform_name = platform.replace(' ', '_')
            
            file_path = os.path.join(self.ETLS_DIR ,'../twitter_html', f'twitter_html_{platform_name}.json')
            with open(file_path, 'w') as json_file:
                json.dump(self.html_source_dict[platform], json_file)

    def main(self):
        # Create advanced searches
        self.create_advanced_search()
        # Make the queries for each platform
        for platform, query in self.advanced_queries.items():
            # Start the brower
            self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self.options) 
            # Open the link on browser
            self.driver.get('https://twitter.com/explore')
            # Login on Twitter account
            self.login_twitter(platform)
            # Make the advanced search
            self.make_search(platform, query)
            print(f"{platform} concluído com sucesso!")
            # Shut down the driver
            self.driver.quit()
        # Export json files with html content
        self.export_html_pages()


if __name__ == "__main__":
    crawler = TwitterCrawler()
    crawler.main()


