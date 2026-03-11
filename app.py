import os
from flask import Flask, render_template, request
import requests
from newspaper import Article
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

NEWS_API_KEY = os.getenv("NEWS_API_KEY")


@app.route('/')
def index():
    page = request.args.get('page', default=1, type=int)
    topic = request.args.get('topic', default=None, type=str)

    articles = fetch_articles(page, topic)

    return render_template(
        'index.html',
        articles=articles,
        page=page,
        topic=topic
    )


def fetch_articles(page, topic=None):

    try:
        page_size = 4   # Number of articles per page

        url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={NEWS_API_KEY}&pageSize={page_size}&page={page}"

        if topic:
            url += f"&category={topic}"

        response = requests.get(url)
        response.raise_for_status()

        data = response.json()

        articles = []

        for article in data['articles']:

            try:
                article_obj = Article(article['url'])
                article_obj.download()
                article_obj.parse()

                articles.append({
                    'title': article['title'],
                    'image': article_obj.top_image,
                    'content': article_obj.text[:100] + "...",
                    'source': article['url'],
                    'timestamp': article['publishedAt']
                })

            except Exception as e:
                print(f"Error processing article: {e}")

        return articles

    except Exception as e:
        print(f"Error fetching articles: {e}")
        return []


if __name__ == "__main__":
    app.run(debug=True)