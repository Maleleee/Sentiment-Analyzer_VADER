# Reddit Sentiment Analyzer

A modern GUI application for analyzing sentiment in Reddit posts using VADER (Valence Aware Dictionary and sEntiment Reasoner) sentiment analysis.

## Features

- Modern, user-friendly GUI interface
- Real-time progress tracking
- Sentiment analysis of Reddit posts and comments
- Export results to CSV
- Beautiful visualization of sentiment distribution
- Support for any public subreddit

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Maleleee/PyBlob_Project.git
cd PyBlob_Project
```

2. Create and activate a virtual environment (recommended):
```bash
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Unix or MacOS:
source venv/bin/activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

4. Set up your Reddit API credentials:
   - Go to https://www.reddit.com/prefs/apps
   - Click "create another app..."
   - Select "script"
   - Fill in the required information
   - Copy the client ID and client secret
   - Create a `.env` file based on `.env.template`:
     ```
     REDDIT_CLIENT_ID=your_client_id_here
     REDDIT_CLIENT_SECRET=your_client_secret_here
     REDDIT_USER_AGENT=your_user_agent_here
     ```

## Usage

1. Run the application:
```bash
python gui.py
```

2. Enter a subreddit name (without the "r/" prefix)
3. Set the number of posts to analyze
4. Click "Start Analysis"
5. View the results in the application
6. Export results to CSV if needed

## Features

- **Modern Interface**: Clean, intuitive design with real-time feedback
- **Progress Tracking**: Visual progress bar and status updates
- **Sentiment Analysis**: Uses VADER for accurate sentiment detection
- **Data Export**: Export results to CSV for further analysis
- **Error Handling**: Clear error messages and troubleshooting tips

## Requirements

- Python 3.8+
- PyQt6
- PRAW
- NLTK
- pandas
- python-dotenv

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

