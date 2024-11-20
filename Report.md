# Hotel Recommender System - Web Mining Project Documentation 

This document explains the implementation of a hotel recommendation system that uses web mining techniques to scrape hotel data from Google Travel and provide personalized recommendations based on user preferences.

## Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Web Mining Implementation](#web-mining-implementation)
4. [Frontend Implementation](#frontend-implementation)
5. [Recommendation Algorithm](#recommendation-algorithm)
6. [Technical Components](#technical-components)

## Project Overview

The Hotel Recommender System is a web application that:
1. Takes user input for a city and preferred hotel features
2. Scrapes real-time hotel data from Google Travel
3. Processes the scraped data
4. Generates personalized hotel recommendations using similarity matching
5. Presents the results in an interactive interface

## Architecture

The project follows a client-server architecture:

- **Backend**: Python Flask server handling web scraping and recommendations
- **Frontend**: HTML/CSS/JavaScript interface for user interaction
- **Key Libraries**:
  - Selenium (web scraping)
  - Flask (server)
  - scikit-learn (similarity calculations)
  - pandas (data processing)

## Web Mining Implementation

### 1. Web Scraping Setup

The project uses Selenium WebDriver to automate the scraping of Google Travel's hotel data. Here's the core scraping setup:

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

def initialize_scraper():
    driver = webdriver.Chrome()
    base_url = 'https://www.google.com/travel/hotels'
    driver.get(base_url)
    return driver
```

### 2. Data Extraction Functions

The project includes several specialized functions to extract different hotel attributes:

```python
def get_hotel_name(div):
    return div.find_element(By.CSS_SELECTOR, '.BgYkof.ogfYpf').text

def get_hotel_rating(div):
    try:
        return div.find_element(By.CSS_SELECTOR, '.lA0BZ').text
    except:
        return 'NA'

def get_hotel_price(div):
    try:
        return div.find_element(By.CSS_SELECTOR, '.kixHKb.flySGb').text
    except:
        return 'NA'

def get_hotel_features(div):
    try:
        features = div.find_elements(By.CSS_SELECTOR, '.bX73z')
        hotel_features = [feature.text for feature in features]
        while len(hotel_features) < 9:
            hotel_features.append('NA')
        return hotel_features
    except:
        return ['NA'] * 9
```

### 3. Web Mining Process Flow

The web mining process follows these steps:

1. **Search Initialization**:
```python
search_bar = driver.find_element(By.CLASS_NAME, 'II2One')
search_bar.clear()
search_bar.send_keys(city)
time.sleep(5)  # Wait for suggestions
```

2. **Data Collection**:
```python
div_elements = driver.find_elements(By.CSS_SELECTOR, '.kCsInf')
hotels_data = []

for div in div_elements:
    hotel_data = {
        'Hotel_Name': get_hotel_name(div),
        'Hotel_Rating': get_hotel_rating(div),
        'Hotel_Price': get_hotel_price(div),
        'City': city,
        'URL': get_hotel_url(div)
    }
    
    # Convert features to binary format
    for feature in selected_features:
        hotel_data[feature] = 1 if feature in features else 0
        
    hotels_data.append(hotel_data)
```

## Recommendation Algorithm

The system uses cosine similarity to match user preferences with hotel features:

```python
from sklearn.metrics.pairwise import cosine_similarity

def generate_recommendations(hotels_df, user_features):
    # Calculate similarity scores
    similarity_scores = cosine_similarity([user_features], 
                                       hotels_df[selected_features])
    
    # Add similarity scores to DataFrame
    hotels_df['Similarity'] = similarity_scores[0]
    
    # Sort and get top recommendations
    recommendations = hotels_df.sort_values(by='Similarity', 
                                          ascending=False).head(10)
    return recommendations
```

## Frontend Implementation

### 1. User Interface

The frontend provides an intuitive interface with:
- City input field
- Feature selection checkboxes
- Results display area with hotel cards

### 2. Dynamic Data Processing

The frontend processes user selections into a binary feature vector:

```javascript
const featureList = [
    "Free breakfast", "Free Wi-Fi", "Air conditioning",
    "Restaurant", "Free parking", "Room service",
    "Pool", "Full-service laundry", "Fitness centre",
    "Kitchen", "Airport shuttle", "Spa"
];

const binaryFeatures = featureList.map(feature => 
    selectedFeatures.includes(feature) ? 1 : 0
);
```

### 3. Results Display

Hotel recommendations are displayed as cards with:
- Hotel name and basic information
- Similarity score
- Direct booking link
- Visual feedback during loading

```javascript
let resultsHTML = '<h2>Recommended Hotels</h2><div class="hotel-list">';
data.forEach(hotel => {
    resultsHTML += `
        <div class="hotel-card">
            <h3>${hotel.Hotel_Name}</h3>
            <p>City: ${hotel.City}</p>
            <p>Rating: ${hotel.Hotel_Rating}</p>
            <p>Price: ${hotel.Hotel_Price}</p>
            <p>Similarity Score: ${(hotel.Similarity * 100).toFixed(2)}%</p>
            <a href="${hotel.URL}" target="_blank" class="book-link">
                Book Now
            </a>
        </div>
    `;
});
```

## Technical Components

### Key Features:
1. **Real-time Data**: The system scrapes live data rather than using a static database
2. **Error Handling**: Robust error handling for web scraping and API responses
3. **Response Processing**: Structured data extraction and transformation
4. **User Experience**: Loading indicators and smooth animations
5. **Responsive Design**: Grid-based layout that adapts to different screen sizes

### Selected Features for Analysis:
```python
selected_features = [
    'Free breakfast', 'Free Wi-Fi', 'Air conditioning',
    'Restaurant', 'Free parking', 'Room service',
    'Pool', 'Full-service laundry', 'Fitness centre',
    'Kitchen', 'Airport shuttle', 'Spa'
]
```

## Conclusion

This web mining project demonstrates the integration of:
- Automated web scraping
- Real-time data processing
- Machine learning-based recommendations
- Interactive user interface

The system provides a practical example of how web mining techniques can be applied to create a useful recommendation system that helps users find hotels matching their preferences.