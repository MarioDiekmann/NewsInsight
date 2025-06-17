import requests
from bs4 import BeautifulSoup as bs
import re
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
from newspaper import Article
import concurrent.futures
from collections import Counter
import spacy
from datetime import datetime
import os
import json
from wordcloud import WordCloud

# Constants
STOPWORDS_FILE = "stopwords.txt"
IMAGE_FOLDER = "static/images/"

# Load NLTK and spaCy German stopwords
german_stopwords = set(stopwords.words('german'))
nlp = spacy.load("de_core_news_sm")
spacy_stopwords = nlp.Defaults.stop_words

# Load external stopword lists
def load_json_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

excluded_links = load_json_file("excluded_links.json")
excluded_words = load_json_file("excluded_words.json")

# Load additional custom stopwords from file
def load_custom_stopwords():
    if os.path.exists(STOPWORDS_FILE):
        with open(STOPWORDS_FILE, "r", encoding="utf-8") as f:
            return set(line.strip().lower() for line in f if line.strip())
    return set()

custom_stopwords = load_custom_stopwords()

# Combine all stopwords into one set
german_stopwords = frozenset(german_stopwords | spacy_stopwords | custom_stopwords)

# Reuse HTTP session for performance
session = requests.Session()


def get_all_article_links(base_url, exclude_set):
    """Extract all valid article links from a newspaper homepage."""
    response = session.get(base_url, timeout=10)
    soup = bs(response.text, 'html.parser')

    links = set()
    for a_tag in soup.find_all('a', href=True):
        link = a_tag['href']
        if link.startswith('/'):
            link = base_url + link
        if link.startswith(base_url) and not any(link.startswith(prefix) for prefix in exclude_set):
            links.add(link)

    return links


def is_paywalled(text):
    """Check whether an article is paywalled based on common keywords."""
    paywall_keywords = {"subscription", "login required", "sign up", "paywall", "exclusive content", "SPIEGEL+"}
    return any(keyword in text.lower() for keyword in paywall_keywords)


def extract_article_text(url):
    """Extract article text using Newspaper3k while skipping paywalls and handling errors."""
    article = Article(url)
    try:
        article.download()
        article.parse()
        return None if is_paywalled(article.text) else article.text
    except:
        return None


def extract_all_articles_from_page(base_url, exclude_set):
    """Download and extract all article texts from a page concurrently."""
    links = get_all_article_links(base_url, exclude_set)
    articles_text = set()

    def process_link(link):
        print(link)
        article_text = extract_article_text(link)
        if article_text:
            articles_text.add(article_text)

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(process_link, links)

    all_words = [word for article in articles_text for word in article.split()]
    return [all_words, list(articles_text)]


def cleanup_list(word_list, domain_stopwords):
    """Clean word list: remove stopwords, non-words, and special characters."""
    word_pattern = re.compile(r'^[a-zA-ZäöüÄÖÜß]+$')
    return [
        word.strip('"')
        for word in word_list
        if word.lower() not in german_stopwords
        and word.lower() not in domain_stopwords
        and word_pattern.match(word)
    ]


def count_word_document_frequency(text_list):
    """Count in how many distinct documents each word appears."""
    word_sets = [set(text.split()) for text in text_list]
    word_doc_count = Counter()
    for word_set in word_sets:
        word_doc_count.update(word_set)
    return word_doc_count


def save_stopwords_to_file():
    """Save current stopwords to disk."""
    with open(STOPWORDS_FILE, "w", encoding="utf-8") as f:
        f.writelines(word + "\n" for word in sorted(german_stopwords))


def find_useless_words(word_counts, num_articles, threshold=0.3):
    """Find words that appear in too many articles."""
    return {word for word, count in word_counts.items() if count / num_articles > threshold}


def add_to_useless_words(url, excluded_links):
    """Update stopwords dynamically based on overused article terms."""
    global german_stopwords
    all_articles = extract_all_articles_from_page(url, excluded_links)[1]
    wordcount_over_articles = count_word_document_frequency(all_articles)
    new_stopwords = find_useless_words(wordcount_over_articles, len(all_articles), threshold=0.2)
    lowercase_useless_words = {word.lower() for word in new_stopwords}
    german_stopwords = frozenset(german_stopwords | lowercase_useless_words)
    save_stopwords_to_file()
    return german_stopwords


def words_to_wordcloud(word_frequencies, save_name):
    """Generate a high-res word cloud image and save it."""
    wordcloud = WordCloud(
        width=4000,
        height=2000,
        background_color="white",
        colormap="viridis"
    ).generate_from_frequencies(word_frequencies)

    os.makedirs(IMAGE_FOLDER, exist_ok=True)
    save_path = os.path.join(IMAGE_FOLDER, save_name)
    wordcloud.to_file(save_path)
    print(f"Wordcloud saved to {save_path}")


def create_all_clouds():
    """Main entry point: scrape all sources, generate word clouds."""
    newspapers = {
        'spiegel': ['https://www.spiegel.de/', excluded_links["spiegel"], excluded_words["spiegel"]],
        'bild': ['https://www.bild.de/', excluded_links["bild"], excluded_words["bild"]],
        'zeit': ['https://www.zeit.de', excluded_links["zeit"], excluded_words["zeit"]],
        'faz': ['https://www.faz.net/aktuell/', excluded_links["faz"], excluded_words["faz"]]
    }

    today = datetime.today().strftime('%Y-%m-%d')

    for name, (url, link_excludes, word_excludes) in newspapers.items():
        words, _ = extract_all_articles_from_page(url, link_excludes)
        filtered = cleanup_list(words, word_excludes)
        word_counts = Counter(filtered).most_common(50)
        words_to_wordcloud(dict(word_counts), f"{name} {today}.png")


if __name__ == '__main__':
    create_all_clouds()
