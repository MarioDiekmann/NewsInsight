from flask import Flask, render_template
import os
from datetime import datetime

app = Flask(__name__)

# Configuration
IMAGE_FOLDER = 'static/images/'


def list_local_images(directory):
    """List all PNG files in a given directory."""
    return [f for f in os.listdir(directory) if f.endswith('.png')]


def generate_image_url(image_name):
    """Return the relative static path for an image."""
    return f'/static/images/{image_name}'


# Load available images
today = datetime.today().strftime('%Y-%m-%d')
image_files = list_local_images(IMAGE_FOLDER)

# Organize images by date and source
wordclouds_data = {}
for image_file in image_files:
    if image_file.endswith('.png'):
        parts = image_file.split(' ')
        newspaper = parts[0]
        date_str = parts[1].split('.')[0]

        if date_str not in wordclouds_data:
            wordclouds_data[date_str] = {}

        wordclouds_data[date_str][newspaper] = generate_image_url(image_file)

# Prepare list of available dates (most recent first)
dates = sorted(wordclouds_data.keys(), reverse=True)


@app.route('/')
def home():
    """Render homepage with today's word clouds."""
    today_wordclouds = wordclouds_data.get(today, {})
    return render_template('index.html', today=today, dates=dates, today_wordclouds=today_wordclouds)


@app.route('/wordclouds/<date>')
def wordclouds(date):
    """Render page with word clouds for a specific date."""
    clouds = wordclouds_data.get(date, {})
    return render_template('wordclouds.html', date=date, dates=dates, wordclouds=clouds)


if __name__ == '__main__':
    app.run(debug=True)
