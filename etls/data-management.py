import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import pandas as pd
from sqlalchemy import create_engine


# Load environment variables from .env file
load_dotenv()

class DataManagement:
    def __init__(self):

        # Create a relative path to the etls directory
        self.ETLS_DIR = os.path.dirname(__file__)

        # Define the html list of pages
        self.html_source_dict = {}
        # Define a list of tweets objects
        self.tweets_list = []
        
        # Import a list with the main streaming platforms
        file_path = os.path.join(self.ETLS_DIR ,'streaming_platforms.json')
        with open(file_path, 'r') as json_file:
            self.streaming_platforms = json.load(json_file)

        # Database connection parameters
        connection_string = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:5432/{os.getenv('DB_DATABASE')}"

        # Create an SQLAlchemy engine and connect to the database:
        self.engine = create_engine(connection_string)
    
    def get_html_pages(self, platform):
        # Create the file_path adding the name of the streaming platform
        file_path = os.path.join(self.ETLS_DIR, '../twitter_html',f"twitter_html_{platform.replace(' ','_')}.json")
        try:
            with open(file_path, 'r', encoding='utf-8') as json_file:
                html_list = json.load(json_file)
                print(f"The {platform} json file was imported successfully!")
            return html_list
        except FileNotFoundError:
            print(f"The file '{file_path}' does not exist.")
        except Exception as e:
            print(f"An error occurred: {str(e)}")
    
    def get_data_from_html(self, html_list, platform):
        # Define a temporary list of tweets
        extracted_tweets = []

        for html_content in html_list:
            # Parse the html page
            soup = BeautifulSoup(html_content, 'html.parser')
            # Get all the div that envolves the tweets
            articles = soup.find_all('article', attrs={'role': 'article'})

            for article in articles:
                div = article.find('div', attrs={'data-testid': 'tweetText'})
                # Get the username of the author
                username = self.get_username(article)
                # Get the tweet text that is spread through span elements
                tweet_text = self.get_text(div)
                # Get timestamp
                timestamp = self.get_timestamp(article)
                
                # Add to tweets a tweet object
                extracted_tweets.append({
                    "text": tweet_text, 
                    "author": username,
                    "created_at": timestamp,
                    "platform": platform
                })
        # Add the tweets objects of the platform analyzed to the tweets_list
        self.tweets_list.extend(extracted_tweets)
        print(f"{platform} data extracted successfully!")
    
    def store_data(self):
        # Create a dataframe and drop the duplicates
        df = pd.DataFrame(self.tweets_list).drop_duplicates()

        # try:
        # Compare the new data with the stored data to avoid duplicates
        df = self.delta_processing(df)
        
        # Insert the dataframe data in the database
        df.to_sql('tweets', self.engine, if_exists='append', index=False, schema='streamings')

        print("New tweets were added!")

        # except Exception as e:
        #     print(f"An error occurred: {str(e)}")

    def delta_processing(self, df):
        # Calculate the date two days ago from today
        two_days_ago = datetime.now() - timedelta(days=2)

        # Format the date in the 'YYYY-MM-DD' format
        formatted_date = two_days_ago.strftime('%Y-%m-%d')

        # Build the query to retrieve data from two days ago until today
        query = f"""
            SELECT "text" FROM streamings.tweets
            WHERE "created_at" >= '{formatted_date}'
        """

        # Query the database to retrieve the data
        existing_records = pd.read_sql_query(query, self.engine)

        # Create a new DataFrame containing only non-duplicate rows
        df_filtered = df[~df['text'].isin(existing_records['text'])]
        print("Delta processing concluded!")

        return df_filtered

    
    def get_username(self, article):
        username_div = article.find('div', class_='css-901oao css-1hf3ou5 r-14j79pv r-18u37iz r-37j5jr r-1wvb978 r-a023e6 r-16dba41 r-rjixqe r-bcqeeo r-qvutc0')
        if username_div:
            username_span = username_div.find('span')
            username = username_span.text
            return username
        
    def get_text(self, div):
        tweet_text = ""
        for span in div.find_all('span'):
            tweet_text += span.text
        return tweet_text

    def get_timestamp(self, article):
        time = article.find('time', attrs={'datetime': True})
        timestamp = time['datetime']
        return timestamp
    
    def main(self):
        for platform in self.streaming_platforms:
            html_list = self.get_html_pages(platform)
            self.get_data_from_html(html_list, platform)
        self.store_data()

if __name__ == "__main__":
    factory = DataManagement()
    factory.main()
