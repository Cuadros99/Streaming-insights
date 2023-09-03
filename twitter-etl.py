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
        self.driver.get('https://twitter.com/explore')
        WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.XPATH,'//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[5]/label/div/div[2]'))  # Replace with the appropriate locator
        )
        self.login_twitter()

    def login_twitter(self):
        login = self.driver.find_element(By.XPATH,'//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[5]/label/div/div[2]')
        login.send_keys(self.login)
        login.send_keys(Keys.RETURN)
        password = self.driver.find_element(By.XPATH,'//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div/div[3]/div/label/div/div[2]/div[1]/input')
        # button = self.driver.find_element(By.XPATH,'//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[6]/div')
        # button.click
        password.send_keys(self.password)
        password.send_keys(Keys.RETURN)

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

