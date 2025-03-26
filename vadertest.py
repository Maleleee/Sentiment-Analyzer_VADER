import praw
import re
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
import csv
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Reddit API credentials from environment variables
CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
USER_AGENT = os.getenv('REDDIT_USER_AGENT')

if not all([CLIENT_ID, CLIENT_SECRET, USER_AGENT]):
    raise ValueError("Missing Reddit API credentials. Please check your .env file.")

# Authenticate with Reddit
reddit = praw.Reddit(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    user_agent=USER_AGENT
)

# Initialize VADER sentiment analyzer
sid = SentimentIntensityAnalyzer()

def clean_text(text, remove_numbers=True, remove_emojis=True):
    """
    Enhanced text cleaning function with configurable options.
    
    Args:
        text (str): Input text to clean
        remove_numbers (bool): Whether to remove numerical digits
        remove_emojis (bool): Whether to remove emoji characters
    """
    if not text:
        return ""
        
    # Remove URLs
    text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
    
    # Remove emoji characters
    if remove_emojis:
        emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
            u"\U00002702-\U000027B0"
            u"\U000024C2-\U0001F251"
            "]+", flags=re.UNICODE)
        text = emoji_pattern.sub(r'', text)
    
    # Remove numbers if specified
    if remove_numbers:
        text = re.sub(r'\d+', '', text)
    
    # Remove special characters but keep apostrophes and quotes
    text = re.sub(r'[^a-zA-Z\s\'\"]', ' ', text)
    
    # Remove extra whitespace and normalize spaces
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def preprocess_text(text, remove_stopwords=True):
    """
    Enhanced text preprocessing with additional options.
    
    Args:
        text (str): Input text to preprocess
        remove_stopwords (bool): Whether to remove common stopwords
    """
    if not text:
        return ""
        
    # Convert to lowercase
    text = text.lower()
    
    if remove_stopwords:
        try:
            # Download stopwords if not already downloaded
            nltk.download('stopwords', quiet=True)
            stop_words = set(nltk.corpus.stopwords.words('english'))
            
            # Remove stopwords
            words = text.split()
            text = ' '.join([word for word in words if word.lower() not in stop_words])
        except Exception as e:
            print(f"Warning: Could not remove stopwords: {str(e)}")
    
    return text

def is_meaningful(text, min_words=3, min_compound_score=0.1):
    """
    Enhanced meaningful text detection with configurable parameters.
    
    Args:
        text (str): Input text to check
        min_words (int): Minimum number of words required
        min_compound_score (float): Minimum absolute compound score to be considered meaningful
    """
    if not text or len(text.split()) < min_words:
        return False
        
    scores = sid.polarity_scores(text)
    # Consider text meaningful if compound score exceeds threshold in either direction
    return abs(scores['compound']) >= min_compound_score

def analyze_sentiment_vader(text):
    """
    Analyzes the sentiment of the input text using VADER.
    Returns a tuple of sentiment (1 for positive, 0 for neutral, -1 for negative)
    and the compound score.
    """
    scores = sid.polarity_scores(text)
    compound = scores['compound']
    # Adjust thresholds if necessary
    if compound > 0.05:
        return 1, compound
    elif compound < -0.05:
        return -1, compound
    else:
        return 0, compound

def fetch_top_posts(subreddit_name, limit=100, min_comment_length=10, progress_callback=None):
    """
    Enhanced post fetching with better error handling and logging.
    """
    try:
        subreddit = reddit.subreddit(subreddit_name)
        top_posts = subreddit.top(limit=limit)
        
        data = []
        processed_posts = 0
        skipped_posts = 0
        
        for post in top_posts:
            try:
                if post.stickied:
                    print(f"Skipping stickied post: {post.title}")
                    skipped_posts += 1
                    continue
                
                # Replace comments.list() with comments.replace_more(limit=0) for better performance
                post.comments.replace_more(limit=0)
                comments = post.comments.list()
                
                valid_comments = [
                    comment for comment in comments 
                    if isinstance(comment, praw.models.Comment) 
                    and comment.author 
                    and comment.author.name.lower() not in ['automoderator']
                    and len(comment.body) >= min_comment_length
                ]
                
                if not valid_comments:
                    print(f"No valid comments found for post: {post.title}")
                    skipped_posts += 1
                    continue
                
                # Sort valid comments by score in descending order
                valid_comments = sorted(valid_comments, key=lambda c: c.score, reverse=True)
                
                # Analyze the highest upvoted valid comment that makes sense
                for comment in valid_comments:
                    cleaned_comment = clean_text(comment.body)
                    preprocessed_comment = preprocess_text(cleaned_comment)
                    if preprocessed_comment and is_meaningful(preprocessed_comment):
                        sentiment, compound = analyze_sentiment_vader(preprocessed_comment)
                        data.append({
                            "title": post.title,
                            "url": f"https://www.reddit.com{post.permalink}",
                            "post_upvotes": post.score,
                            "comment_text": preprocessed_comment,
                            "comment_upvotes": comment.score,
                            "sentiment": sentiment,
                            "compound": compound
                        })
                        break  # Move to the next post after finding a valid comment
                
                processed_posts += 1
                if progress_callback:
                    progress_callback(processed_posts)
                
            except Exception as e:
                print(f"Error processing post {post.title}: {str(e)}")
                skipped_posts += 1
                continue
        
        print(f"\nProcessing Summary:")
        print(f"Successfully processed: {processed_posts} posts")
        print(f"Skipped posts: {skipped_posts}")
        
        return data
        
    except Exception as e:
        print(f"Error accessing subreddit {subreddit_name}: {str(e)}")
        return []

def calculate_metrics(data):
    """
    Calculates various metrics for the sentiment analysis results.
    Returns a dictionary containing different metrics.
    """
    if not data:
        return {
            "total_posts": 0,
            "positive_ratio": 0,
            "negative_ratio": 0,
            "neutral_ratio": 0,
            "avg_compound": 0
        }
    
    total = len(data)
    positive_count = sum(1 for entry in data if entry["sentiment"] == 1)
    negative_count = sum(1 for entry in data if entry["sentiment"] == -1)
    neutral_count = sum(1 for entry in data if entry["sentiment"] == 0)
    
    avg_compound = sum(abs(entry["compound"]) for entry in data) / total
    
    return {
        "total_posts": total,
        "positive_ratio": (positive_count / total) * 100,
        "negative_ratio": (negative_count / total) * 100,
        "neutral_ratio": (neutral_count / total) * 100,
        "avg_compound": avg_compound
    }

def save_to_csv(data, filename="sentiment_analysis_results_VADER.csv"):
    """
    Saves the sentiment analysis results to a CSV file, sorted by post upvotes.
    
    Args:
        data (list): List of dictionaries containing the analysis results
        filename (str): Name of the output CSV file
    """
    if not data:
        print("No data to save to CSV")
        return
        
    # Sort by post_upvotes instead of comment_upvotes
    data = sorted(data, key=lambda x: x['post_upvotes'], reverse=True)
    
    keys = data[0].keys()
    with open(filename, 'w', newline='', encoding='utf-8') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)
    
    print(f"Data saved to {filename}, sorted by post upvotes in descending order")

def main():
    # Configuration
    config = {
        'subreddit_name': "controlproblem",
        'post_limit': 100,
        'min_comment_length': 10,
        'min_words': 3,
        'min_compound_score': 0.1,
        'remove_stopwords': True,
        'remove_numbers': True,
        'remove_emojis': True
    }
    
    print(f"Starting analysis of r/{config['subreddit_name']}...")
    
    posts_data = fetch_top_posts(
        config['subreddit_name'], 
        limit=config['post_limit'],
        min_comment_length=config['min_comment_length']
    )
    
    metrics = calculate_metrics(posts_data)
    print(f"\nResults:")
    print(f"Analyzed {metrics['total_posts']} posts")
    print(f"Sentiment Distribution:")
    print(f"  Positive: {metrics['positive_ratio']:.1f}%")
    print(f"  Negative: {metrics['negative_ratio']:.1f}%")
    print(f"  Neutral: {metrics['neutral_ratio']:.1f}%")
    print(f"Average Compound Score: {metrics['avg_compound']:.3f}")
    
    save_to_csv(posts_data)

if __name__ == "__main__":
    main()