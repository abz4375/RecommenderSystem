from flask import Flask, request, jsonify
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from sklearn.metrics.pairwise import cosine_similarity
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import pandas as pd
import time
import logging
import colorlog

# Set up colorized logging
handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
    '%(log_color)s%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white',
    }
))

logger = colorlog.getLogger('HotelRecommender')
logger.addHandler(handler)
logger.setLevel(logging.INFO)

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
        logger.info('╔════════════════════════════════════════════════╗')
        logger.info('║         Starting Hotel Recommendation          ║')
        logger.info('╚════════════════════════════════════════════════╝')
        
        data = request.json
        city = data.get('city')
        user_features = data.get('features')
        
        logger.info(f'🌍 Processing request for city: {city}')
        
        # Chrome setup
        logger.info('🔧 Configuring Chrome options...')
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-notifications')
        chrome_options.add_argument('--disable-infobars')
        
        logger.info('🚀 Launching Chrome driver...')
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(100)
        
        base_url = 'https://www.google.com/travel/hotels'
        try:
            logger.info('🌐 Navigating to Google Hotels...')
            driver.get(base_url)
        except TimeoutException:
            logger.error('❌ Page load timeout')
            driver.quit()
            return jsonify({'error': 'Page load timeout'}), 408
        
        logger.info(f'🔍 Searching for hotels in {city}...')
        search_bar = driver.find_element(By.CLASS_NAME, 'II2One')
        search_bar.clear()
        search_bar.send_keys(city)
        time.sleep(5)
        
        actions = ActionChains(driver)
        actions.send_keys(Keys.RETURN)
        actions.perform()
        logger.info('⏳ Waiting for results to load...')
        time.sleep(10)

        logger.info('📊 Collecting hotel data...')
        hotels_data = []
        div_elements = driver.find_elements(By.CSS_SELECTOR, '.kCsInf')
        
        selected_features = ['Free breakfast', 'Free Wi-Fi', 'Air conditioning', 'Restaurant', 
                           'Free parking', 'Room service', 'Pool', 'Full-service laundry', 
                           'Fitness centre', 'Kitchen', 'Airport shuttle', 'Spa']
                           
        logger.info(f'Found {len(div_elements)} hotels to process')
        
        for i, div in enumerate(div_elements, 1):
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
                
                for feature in selected_features:
                    hotel_data[feature] = 1 if feature in features else 0
                    
                hotels_data.append(hotel_data)
                logger.info(f'✅ Processed hotel {i}/{len(div_elements)}: {hotel_name}')
            except Exception as e:
                logger.warning(f'⚠️ Failed to process hotel {i}: {str(e)}')
                continue
                
        driver.quit()
        logger.info(f'🎯 Successfully collected {len(hotels_data)} hotels')
        
        if not hotels_data:
            logger.error('❌ No hotels found in the specified city')
            return jsonify({'error': 'No hotels found in the specified city'}), 404
            
        logger.info('🧮 Calculating similarity scores...')
        df = pd.DataFrame(hotels_data)
        similarity_scores = cosine_similarity([user_features], df[selected_features])
        df['Similarity'] = similarity_scores[0]
        
        recommendations = df.sort_values(by='Similarity', ascending=False).head(10)
        logger.info(f'✨ Generated top {len(recommendations)} recommendations')
        
        logger.info('╔════════════════════════════════════════════════╗')
        logger.info('║         Recommendation Process Complete         ║')
        logger.info('╚════════════════════════════════════════════════╝')
        
        return jsonify(recommendations.to_dict('records'))
        
    except Exception as e:
        logger.error(f'❌ Error during processing: {str(e)}')
        return jsonify({'error': str(e)}), 500
    finally:
        if 'driver' in locals():
            driver.quit()
            logger.info('🚪 Chrome driver closed')

if __name__ == '__main__':
    logger.info('🚀 Starting Hotel Recommender Server...')
    app.run(debug=True, port=5000)