import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                            QSpinBox, QProgressBar, QTextEdit, QFrame,
                            QMessageBox, QFileDialog, QGroupBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QPalette, QColor, QFont
from vadertest import fetch_top_posts as vader_fetch
import pandas as pd

class ModernButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)

class ModernLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #cccccc;
                border-radius: 4px;
                background-color: white;
                color: #333333;
            }
            QLineEdit:focus {
                border: 1px solid #4CAF50;
            }
        """)

class ModernSpinBox(QSpinBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QSpinBox {
                padding: 8px;
                border: 1px solid #cccccc;
                border-radius: 4px;
                background-color: white;
                color: #333333;
            }
            QSpinBox:focus {
                border: 1px solid #4CAF50;
            }
        """)

class ModernProgressBar(QProgressBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QProgressBar {
                border: 1px solid #cccccc;
                border-radius: 4px;
                text-align: center;
                background-color: #f0f0f0;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 3px;
            }
        """)

class ModernTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QTextEdit {
                background-color: white;
                color: #333333;
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 8px;
            }
            QTextEdit:focus {
                border: 1px solid #4CAF50;
            }
        """)

class AnalysisWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(list)
    error = pyqtSignal(str)
    status = pyqtSignal(str)

    def __init__(self, subreddit, limit):
        super().__init__()
        self.subreddit = subreddit
        self.limit = limit

    def run(self):
        try:
            self.status.emit("Fetching posts from Reddit...")
            data = vader_fetch(self.subreddit, limit=self.limit, progress_callback=self.progress.emit)
            self.finished.emit(data)
        except Exception as e:
            self.error.emit(str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Reddit Sentiment Analyzer (VADER)")
        self.setMinimumSize(1000, 800)
        
        # Set light theme with accent colors
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QLabel {
                color: #333333;
            }
            QGroupBox {
                color: #333333;
                border: 1px solid #cccccc;
                border-radius: 4px;
                margin-top: 1em;
                padding-top: 1em;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px;
                color: #4CAF50;
                font-weight: bold;
            }
        """)
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Input section
        input_group = QGroupBox("Analysis Settings")
        input_layout = QHBoxLayout()
        
        # Subreddit input
        subreddit_layout = QVBoxLayout()
        subreddit_label = QLabel("Subreddit:")
        subreddit_label.setStyleSheet("font-weight: bold; color: #333333;")
        self.subreddit_input = ModernLineEdit()
        self.subreddit_input.setPlaceholderText("Enter subreddit name")
        subreddit_layout.addWidget(subreddit_label)
        subreddit_layout.addWidget(self.subreddit_input)
        
        # Post limit
        limit_layout = QVBoxLayout()
        limit_label = QLabel("Number of Posts:")
        limit_label.setStyleSheet("font-weight: bold; color: #333333;")
        self.limit_spin = ModernSpinBox()
        self.limit_spin.setRange(1, 1000)
        self.limit_spin.setValue(100)
        limit_layout.addWidget(limit_label)
        limit_layout.addWidget(self.limit_spin)
        
        # Add all input widgets to input layout
        input_layout.addLayout(subreddit_layout)
        input_layout.addLayout(limit_layout)
        input_group.setLayout(input_layout)
        
        # Analysis button
        self.analyze_button = ModernButton("Start Analysis")
        self.analyze_button.clicked.connect(self.start_analysis)
        
        # Status section
        status_group = QGroupBox("Status")
        status_layout = QVBoxLayout()
        
        # Status label
        self.status_label = QLabel("Ready to analyze")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #666666;")
        
        # Progress bar
        self.progress_bar = ModernProgressBar()
        self.progress_bar.setVisible(False)
        
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.progress_bar)
        status_group.setLayout(status_layout)
        
        # Results section
        results_group = QGroupBox("Analysis Results")
        results_layout = QVBoxLayout()
        
        # Results display
        self.results_text = ModernTextEdit()
        self.results_text.setReadOnly(True)
        
        # Export button
        self.export_button = ModernButton("Export to CSV")
        self.export_button.clicked.connect(self.export_results)
        self.export_button.setEnabled(False)
        
        results_layout.addWidget(self.results_text)
        results_layout.addWidget(self.export_button)
        results_group.setLayout(results_layout)
        
        # Add all sections to main layout
        layout.addWidget(input_group)
        layout.addWidget(self.analyze_button)
        layout.addWidget(status_group)
        layout.addWidget(results_group)
        
        self.analysis_data = None

    def start_analysis(self):
        subreddit = self.subreddit_input.text().strip()
        if not subreddit:
            QMessageBox.warning(self, "Error", "Please enter a subreddit name")
            return
            
        self.analyze_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, self.limit_spin.value())
        self.progress_bar.setValue(0)
        self.status_label.setText("Starting analysis...")
        self.results_text.clear()
        
        self.worker = AnalysisWorker(
            subreddit,
            self.limit_spin.value()
        )
        self.worker.finished.connect(self.analysis_complete)
        self.worker.error.connect(self.analysis_error)
        self.worker.progress.connect(self.update_progress)
        self.worker.status.connect(self.update_status)
        self.worker.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def update_status(self, message):
        self.status_label.setText(message)

    def analysis_complete(self, data):
        self.analysis_data = data
        self.progress_bar.setVisible(False)
        self.status_label.setText("Analysis complete!")
        self.analyze_button.setEnabled(True)
        self.export_button.setEnabled(True)
        
        # Display results
        self.results_text.clear()
        
        if not data:
            self.results_text.append("No data was retrieved from the subreddit.")
            self.results_text.append("\nPossible reasons:")
            self.results_text.append("1. The subreddit name might be incorrect")
            self.results_text.append("2. The subreddit might be private or restricted")
            self.results_text.append("3. There might be no posts matching the criteria")
            self.results_text.append("4. There might be an issue with the Reddit API credentials")
            return
            
        self.results_text.append(f"Analysis complete! Found {len(data)} posts.\n\n")
        
        # Calculate and display statistics
        positive = sum(1 for post in data if post["sentiment"] == 1)
        negative = sum(1 for post in data if post["sentiment"] == -1)
        neutral = sum(1 for post in data if post["sentiment"] == 0)
        
        self.results_text.append("Sentiment Distribution:")
        self.results_text.append(f"Positive: {positive} ({positive/len(data)*100:.1f}%)")
        self.results_text.append(f"Negative: {negative} ({negative/len(data)*100:.1f}%)")
        self.results_text.append(f"Neutral: {neutral} ({neutral/len(data)*100:.1f}%)\n")
        
        # Display sample posts
        self.results_text.append("Sample Posts:")
        for post in data[:5]:
            sentiment = "Positive" if post["sentiment"] == 1 else "Negative" if post["sentiment"] == -1 else "Neutral"
            sentiment_color = "#4CAF50" if sentiment == "Positive" else "#f44336" if sentiment == "Negative" else "#666666"
            self.results_text.append(f"\nTitle: {post['title']}")
            self.results_text.append(f'<span style="color: {sentiment_color}">Sentiment: {sentiment}</span>')
            self.results_text.append(f"Score: {post['post_upvotes']}")
            self.results_text.append(f"Compound Score: {post['compound']:.3f}")
            self.results_text.append("-" * 50)

    def analysis_error(self, error_msg):
        self.progress_bar.setVisible(False)
        self.analyze_button.setEnabled(True)
        QMessageBox.critical(self, "Error", f"Analysis failed: {error_msg}")

    def export_results(self):
        if not self.analysis_data:
            return
            
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save Results",
            "",
            "CSV Files (*.csv)"
        )
        
        if filename:
            try:
                df = pd.DataFrame(self.analysis_data)
                df.to_csv(filename, index=False)
                QMessageBox.information(self, "Success", "Results exported successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export results: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec()) 