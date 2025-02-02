import praw
import re
from nltk.corpus import stopwords
from textblob import TextBlob
import nltk
import csv

# Download necessary NLTK data files
nltk.download('stopwords')

# Reddit API credentials
CLIENT_ID = # Enter your client ID here
CLIENT_SECRET = ## Enter client secret here
USER_AGENT = ## This is just a description

# Authenticate with Reddit
reddit = praw.Reddit(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    user_agent=USER_AGENT
)

def clean_text(text):
    """
    Cleans the input text by removing URLs and special characters.
    """
    # Remove URLs
    text = re.sub(r'http\S+', '', text)
    # Remove non-alphanumeric characters
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    return text

def correct_grammar(text):
    """
    Corrects the capitalization and grammar of the input text using TextBlob.
    """
    blob = TextBlob(text)
    corrected_text = str(blob.correct())
    return corrected_text

def preprocess_text(text):
    """
    Converts the text to lowercase and removes stopwords.
    """
    # Convert to lowercase
    text = text.lower()
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    words = text.split()
    cleaned_text = ' '.join([word for word in words if word not in stop_words])
    return cleaned_text

def is_meaningful(text):
    """
    Checks if the text is meaningful using TextBlob's subjectivity score.
    """
    blob = TextBlob(text)
    # Subjectivity ranges from 0 (very objective) to 1 (very subjective)
    # We assume a comment is meaningful if its subjectivity is above a threshold
    return blob.sentiment.subjectivity > 0.1

def analyze_sentiment(text):
    """
    Analyzes the sentiment of the input text using TextBlob.
    Returns a tuple of sentiment (1 for positive, 0 for neutral, -1 for negative)
    and the polarity score.
    """
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    # Adjust thresholds if necessary
    if polarity > 0.1:
        return 1, polarity
    elif polarity < -0.1:
        return -1, polarity
    else:
        return 0, polarity

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
            corrected_comment = correct_grammar(cleaned_comment)
            preprocessed_comment = preprocess_text(corrected_comment)
            if preprocessed_comment and len(preprocessed_comment.split()) > 5 and is_meaningful(preprocessed_comment):
                sentiment, polarity = analyze_sentiment(preprocessed_comment)
                data.append({
                    "title": post.title,
                    "url": f"https://www.reddit.com{post.permalink}",
                    "post_upvotes": post.score,
                    "comment_text": preprocessed_comment,
                    "comment_upvotes": comment.score,
                    "sentiment": sentiment,
                    "polarity": polarity
                })
                break  # Move to the next post after finding a valid comment
    
    return data

def calculate_accuracy(data):
    """
    Calculates the accuracy of the sentiment analysis based on the polarity scores.
    """
    correct_predictions = sum(1 for entry in data if (entry["polarity"] > 0 and entry["sentiment"] == 1) or
                                                      (entry["polarity"] < 0 and entry["sentiment"] == -1) or
                                                      (entry["polarity"] == 0 and entry["sentiment"] == 0))
    accuracy = (correct_predictions / len(data)) * 100 if data else 0
    return accuracy

def save_to_csv(data, filename="sentiment_analysis_results.csv"):
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
    limit = 500  # Increase limit for more posts
    posts_data = fetch_top_posts(subreddit_name, limit=limit)
    
    accuracy = calculate_accuracy(posts_data)
    print(f"Analyzed {len(posts_data)} posts from r/{subreddit_name} with an accuracy of {accuracy:.2f}%")
    
    save_to_csv(posts_data)

if __name__ == "__main__":
    main()
