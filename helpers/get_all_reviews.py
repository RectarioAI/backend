import time
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def reviews_scrapping(driver):
    reviews_list = []
    try:
        try:
            cookie_banner = driver.find_element(By.CLASS_NAME, "cookie-consent-banner-opt-out__action")
            cookie_banner.click()
            time.sleep(1)
        except:
            pass

        show_more_button = driver.find_element(By.CLASS_NAME, "show-more-click")
        show_more_button.click()

        time.sleep(3)

        WebDriverWait(driver, 3).until(
            EC.frame_to_be_available_and_switch_to_it((By.ID, "ui-pdp-iframe-reviews"))
        )

        iframe_html = driver.page_source
        soup = BeautifulSoup(iframe_html, 'html.parser')
        
        total_opinions_element = soup.find("span", class_="total-opinion")
        if total_opinions_element:
            total_opinions_text = total_opinions_element.text.strip()
            total_opinions = int(total_opinions_text.split()[0])
        else:
            print("No se pudo encontrar el total de opiniones.")
            total_opinions = None

        last_count = 0
        current_count = 0

        while total_opinions is None or current_count < total_opinions:

            iframe_html = driver.page_source
            soup = BeautifulSoup(iframe_html, 'html.parser')

            reviews = soup.find_all("article", {'aria-roledescription': "Review"})

            current_count = len(reviews)

            if current_count == last_count:
                print("No se cargaron más reseñas. Deteniendo el desplazamiento.")
                break
            
            last_count = current_count

            driver.execute_script("window.scrollBy(0, 5000);")  
            time.sleep(2)

        if reviews:
            for review_element in reviews:
                    review_text = review_element.find('p', {'class': 'ui-review-capability-comments__comment__content ui-review-capability-comments__comment__content'}).text  

                    reviews_list.append(review_text)  
            else:
                print('No hay reviews disponibles ')
        driver.quit()

    except Exception as e:
        print(f"Error: {e}")
        driver.quit()

    return reviews_list 