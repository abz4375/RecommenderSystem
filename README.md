# Hotel Recommender System

A hotel recommendation engine that scrapes live hotel listings from Google Travel and ranks them against a user's preferences using cosine similarity.

## Why

Hotel search sites let you filter by amenity, but they don't rank results by how well the *combination* of amenities, price, and rating matches what you actually care about. This project scrapes real listings for a given city and scores them with a weighted similarity model instead of a flat filter.

## Features

- Scrapes live hotel data (name, price, rating, amenities, URL) from Google Travel using Selenium
- Converts amenities into a binary feature vector and ranks hotels by cosine similarity against the user's selected preferences
- Weighted scoring that blends feature similarity, price (lower is better), and rating — not just raw similarity
- Filters across 12 amenities: free breakfast, Wi-Fi, air conditioning, restaurant, parking, room service, pool, laundry, fitness centre, kitchen, airport shuttle, spa
- Flask API backend with a static HTML/CSS frontend

## Architecture

```
Browser (index.html) ── POST /recommend ──▶ Flask API (app.py)
                                                   │
                                     Selenium launches headless Chrome
                                                   │
                                    Scrapes live listings from Google Travel
                                                   │
                              Binary feature vectors + cosine similarity (scikit-learn)
                                                   │
                          Weighted score = similarity + price + rating (pandas)
                                                   │
                                     Top 10 ranked results ──▶ JSON response
```

## Tech Stack

Python, Flask, Selenium, scikit-learn, pandas, HTML/CSS

## Local Setup

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

The API serves on `http://localhost:8080`. Open `index.html` in a browser to use the UI.

## Future Improvements

- Cache scraped results per city to avoid re-scraping on every request
- Replace the hand-tuned price/rating weighting with a learned ranking model
- Add pagination for cities with a large number of listings

---

Project source: [github.com/abz4375/RecommenderSystem](https://github.com/abz4375/RecommenderSystem)
