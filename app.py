from flask import Flask, request, jsonify
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import time

app = Flask(__name__)
CORS(app)

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

def get_hotel_url(div):
    try:
        return div.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
    except:
        return 'NA'


@app.route('/recommend', methods=['POST'])
def get_recommendations():
    try:
        data = request.json
        city = data.get('city')
        user_features = data.get('features')
        
        # Initialize webdriver
        driver = webdriver.Chrome()
        base_url = 'https://www.google.com/travel/hotels'
        driver.get(base_url)
        
        # Search for city
        search_bar = driver.find_element(By.CLASS_NAME, 'II2One')
        search_bar.clear()
        search_bar.send_keys(city)
        time.sleep(5)
        
        actions = ActionChains(driver)
        actions.send_keys(Keys.RETURN)
        actions.perform()
        time.sleep(10)

        # Scrape hotel data
        hotels_data = []
        div_elements = driver.find_elements(By.CSS_SELECTOR, '.kCsInf')
        
        selected_features = ['Free breakfast', 'Free Wi-Fi', 'Air conditioning', 'Restaurant', 
                           'Free parking', 'Room service', 'Pool', 'Full-service laundry', 
                           'Fitness centre', 'Kitchen', 'Airport shuttle', 'Spa']

        for div in div_elements:
            try:
                hotel_name = get_hotel_name(div)
                hotel_rating = get_hotel_rating(div)
                hotel_price = get_hotel_price(div)
                features = get_hotel_features(div)
                hotel_url = get_hotel_url(div)
                
                hotel_data = {
                    'Hotel_Name': hotel_name,
                    'Hotel_Rating': hotel_rating,
                    'Hotel_Price': hotel_price,
                    'City': city,
                    'URL': hotel_url,
                }
                
                # Convert features to binary format
                for feature in selected_features:
                    hotel_data[feature] = 1 if feature in features else 0
                    
                hotels_data.append(hotel_data)
            except Exception as e:
                continue
                
        driver.quit()
        
        if not hotels_data:
            return jsonify({'error': 'No hotels found in the specified city'}), 404
            
        # Convert to DataFrame and calculate similarities
        df = pd.DataFrame(hotels_data)
        similarity_scores = cosine_similarity([user_features], df[selected_features])
        df['Similarity'] = similarity_scores[0]
        
        # Sort and return top recommendations
        recommendations = df.sort_values(by='Similarity', ascending=False).head(10)
        return jsonify(recommendations.to_dict('records'))
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if 'driver' in locals():
            driver.quit()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
