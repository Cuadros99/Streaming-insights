import os
from dotenv import load_dotenv
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


from bs4 import BeautifulSoup

# Load environment variables from .env file
load_dotenv()


# Define the keywords you want to search for

class TwitterCrawler:
    def __init__(self):
        # Initialize Selenium (you'll need to specify your web driver, e.g., ChromeDriver)
        options = Options()
        options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)  # Specify the path to your ChromeDriver executable
        # Keywords
        self.keywords = ["bom", "ruim", "chato", "legal", "amo", "odeio", "muito", "pouco", "maratona", "maratonando", "assistir", "assistindo", "vsf", "lol", "mds", "foda", "merda", "tnc", "site", "aplicativo", "player", "lixo", "pqp", "app", "curtindo", "curti", "otimo", "maravilhoso", "maravilhosa", "horrivel", "bosta", "coco", "melhor","pior", "adoro", "caro", "cara","barato"]
        # List of the main streaming platforms
        self.streaming_platforms = ["Disney Plus", "Netflix", "HBO Max", "Amazon Prime", "Prime Video", "Apple TV", "Paramount+", "Globoplay", "Star Plus"]
        # Define the common filters
        self.common_filters = "-filter:links -filter:replies"
        # Define the period (since:2023-08-01)
        self.period = "since:2023-08-01"
        # Define the language (lang:pt)
        self.language = "lang:pt"
        # Define the minimum favorites and retweets
        self.engagement = "min_faves:300 min_retweets:5"

        self.login = os.getenv('TWITTER_LOGIN')
        self.username = os.getenv('TWITTER_USERNAME')
        self.password = os.getenv('TWITTER_PASS')

    # Create advanced search queries for each streaming platform
    def create_advanced_search(self):
        self.advanced_queries = []
        for platform in self.streaming_platforms:
            # Construct the query for mentioned accounts
            keywords_query = " OR ".join(self.keywords)

            # Combine all components to create the advanced search query
            search_query = f'{platform} ({keywords_query}) {self.language} {self.period} {self.common_filters}'

            # Add the query to the advances queries list
            self.advanced_queries.append(search_query)

    def get_html_pages(self):
        self.create_advanced_search()
        self.driver.get('https://twitter.com/explore')
        self.login_twitter()
        self.make_search(self.advanced_queries[0])

    def login_twitter(self):
        try:
            self.insert_text(self.login, '//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[5]/label/div/div[2]/div/input' )
            self.insert_text(self.username, '//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div[2]/label/div/div[2]/div/input', 5)
            self.insert_text(self.password, '//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div/div[3]/div/label/div/div[2]/div[1]/input',40)
        except Exception as e:
            print("An unexpected error occurred:", e)

    def insert_text(self, text, XPATH, timeout=10):
        input_text = self.wait_for_element(XPATH)
        if input_text:
            input_text.send_keys(text)
            input_text.send_keys(Keys.RETURN)

    def wait_for_element(self, locator, by_type = By.XPATH, timeout=30):
        element = WebDriverWait(self.driver, timeout).until( EC.presence_of_element_located((by_type,locator)))
        return element

    def make_search(self, adv_search):
        try:
            # Enter in the Explore Tab
            self.wait_for_element('//*[@id="react-root"]/div/div/div[2]/header/div/div/div/div[1]/div[2]/nav/a[2]/div').click()
            # Insert text in the search bar 
            self.insert_text(adv_search, '//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div[1]/div[1]/div[1]/div/div/div/div/div[1]/div[2]/div/div/div/form/div[1]/div/div/div/label/div[2]/div/input',90)
            # Enter in the Latest Tab
            self.wait_for_element('//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div[1]/div[1]/div[2]/nav/div/div[2]/div/div[2]/a').click()
            # Scroll down to load more tweets
            self.scroll_down()
            # Shut down the driver
            self.driver.quit()

        except Exception as e:
            print("An unexpected error occurred:", e)
        
    def scroll_down(self, target_tweets_count = 300, scroll_pause_time = 1.5):
        self.wait_for_element('div[data-testid="cellInnerDiv"]', By.CSS_SELECTOR)
        # Count the number of tweets on the page
        tweets_count = len(self.driver.find_elements(By.CSS_SELECTOR, 'div[data-testid="cellInnerDiv"]'))

        # Get scroll height
        last_height = self.driver.execute_script("return document.body.scrollHeight")

        while tweets_count < target_tweets_count:
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
        
        html_source = self.driver.page_source

        with open('twitter_html_source.txt', 'w', encoding='utf-8') as file:
            file.write(html_source)



# style="transform: translateY(39183px); position: absolute; width: 100%; transition: opacity 0.3s ease-out 0s;"
# data-testid="tweet"
# data-testid="tweetText"





# Example Usage:
if __name__ == "__main__":
    crawler = TwitterCrawler()
    # crawler.create_advanced_search()
    crawler.get_html_pages()


# Examples of advanced searches
    # "Disney Plus" (bom OR ruim OR foda OR merda OR tnc OR vsf) lang:pt since:2023-08-01 -filter:links -filter:replies
    # "Disney Plus" (bom OR ruim OR foda OR merda OR tnc OR vsf) lang:pt since:2023-08-01 -filter:links -filter:replies


# ESTRUTURA DA CONSULTA AVANÇADA
# Keywords 
# ("word1" OR "word2")  

# Engagement
# min_faves:100 min_retweets:50

# Filters
# -filter:links -filter:replies

# Period
# until:2023-10-31 since:2023-08-01 

# Metioned accounts
# (@netflix OR @NetflixBrasil OR @DisneyPlus) 

# Language
# lang:pt 

