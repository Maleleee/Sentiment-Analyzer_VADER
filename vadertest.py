import praw
import re
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
import csv

# Download necessary NLTK data files
nltk.download('vader_lexicon')

# Reddit API credentials
CLIENT_ID = 'dzq6IR-rrxodp6T7RK-6hw'
CLIENT_SECRET = 'D-PKWOBJUiFOsjQLFTapR7Dcp33-tQ'
USER_AGENT = 'Pyblob by Malele'

# Authenticate with Reddit
reddit = praw.Reddit(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    user_agent=USER_AGENT
)

# Initialize VADER sentiment analyzer
sid = SentimentIntensityAnalyzer()

def clean_text(text):
    """
    Cleans the input text by removing URLs and special characters, but retains quotes.
    """
    # Remove URLs
    text = re.sub(r'http\S+', '', text)
    # Remove non-alphanumeric characters except for spaces, newlines, and quotes
    text = re.sub(r'[^a-zA-Z\s\n\'\"]', '', text)
    return text

def preprocess_text(text):
    """
    Converts the text to lowercase.
    """
    # Convert to lowercase
    text = text.lower()
    return text

def is_meaningful(text):
    """
    Checks if the text is meaningful using VADER's compound score.
    """
    scores = sid.polarity_scores(text)
    # We assume a comment is meaningful if its compound score is not neutral
    return scores['compound'] != 0

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

def fetch_top_posts(subreddit_name, limit=100):
    """
    Fetches the top posts from a given subreddit, analyzes the most upvoted
    comment from each post, and returns the results.
    """
    subreddit = reddit.subreddit(subreddit_name)
    top_posts = subreddit.top(limit=limit)
    
    data = []
    for post in top_posts:
        if post.stickied:
            print(f"Skipping stickied post: {post.title}")
            continue
        
        comments = post.comments.list()
        # Filter out MoreComments objects and invalid comments
        valid_comments = [comment for comment in comments if isinstance(comment, praw.models.Comment)]
        
        if not valid_comments:
            print(f"No valid comments found for post: {post.title}")
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
    
    return data

def calculate_accuracy(data):
    """
    Calculates the accuracy of the sentiment analysis based on the compound scores.
    """
    correct_predictions = sum(1 for entry in data if (entry["compound"] > 0 and entry["sentiment"] == 1) or
                                                      (entry["compound"] < 0 and entry["sentiment"] == -1) or
                                                      (entry["compound"] == 0 and entry["sentiment"] == 0))
    accuracy = (correct_predictions / len(data)) * 100 if data else 0
    return accuracy

def save_to_csv(data, filename="sentiment_analysis_results_VADER.csv"):
    """
    Saves the sentiment analysis results to a CSV file, sorted by comment upvotes.
    """
    data = sorted(data, key=lambda x: x['comment_upvotes'], reverse=True)
    keys = data[0].keys()
    with open(filename, 'w', newline='', encoding='utf-8') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)

def main():
    subreddit_name = "controlproblem"  # Change to your target subreddit
    limit = 100  # Analyze the top 100 posts
    posts_data = fetch_top_posts(subreddit_name, limit=limit)
    
    accuracy = calculate_accuracy(posts_data)
    print(f"Analyzed {len(posts_data)} posts from r/{subreddit_name} with an accuracy of {accuracy:.2f}%")
    
    save_to_csv(posts_data)

if __name__ == "__main__":
    main()