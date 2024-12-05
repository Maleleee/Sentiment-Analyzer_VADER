## Sentiment Analysis for Reddit using VADER

# Overview

This repository provides a Python script for analyzing sentiments in Reddit comments using VADER (Valence Aware Dictionary and sEntiment Reasoner) sentiment analyzer. The script fetches the top posts from a specified subreddit, extracts the most upvoted 
meaningful comment from eahc post, and determines the sentiment as positive, neutral, or negative. The results are saved to a CSV 
file for further analysis.

# Features

* Reddit API Integration: Utilizes the PRAW library to fetch top posts and comments from Reddit.
* Sentiment Analysis: Employs NLTK's VANDER sentiment analyzer to classify text sentiment and provide compound scores.
* Text Cleaning and Preprocessing: Removes URLs, special characters, and extra whitspace while retaining meaningful content.

# Installation

1. Clone the repository using

* git clone https://github.com/Maleleee/reddit-sentiment-analysis.git
* cd reddit-sentiment-analysis

2. Install the required libraries.

* pip install praw nltk

3. Download the necessary NLTK data files:

* import nltk 
* nltk.download ('vader_lexicon')

4. Configure your Reddit API credentials by replacing the placeholders in the script: 

CLIENT_ID = 'your_client_id'
CLIENT_SECRET = 'your_client_secret'
USER_AGENT = 'your_user_agent'


# Usage

1. Set the Target Subreddit

Update the subreddit_name variable in the main() function to the subreddit you want to analyze:

* subreddit_name = 'target_subreddit'

2. Run the script

Execute the script to fetch, process, and analyze Reddit data:

* python enterscriptnamehere.py

3. View the Results

The analysis results will be saved in a CSV file named sentiment_analysis_results_VADER.csv, which includes the ff:

* Post title
* Post URL
* Post upvotes
* Comment text
* Comment upvotes
* Sentiment classification (Positive, Neutral, Negative)
* Compound sentiment score

## Dependencies

* Python 3.8+
* PRAW
* NLTK

## Contributions 

Contributions, issues, and feature requests are welcome! Feel free to fork this repository and submit a pull request.

