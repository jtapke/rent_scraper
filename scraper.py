# import packages
from time import sleep # to pause for-loop every loop
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import re #for using regex

class ApartmentScraper:
    def __init__(self, url):
        self.url = url
        self.service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=self.service)
        self.data = []

    def scrape(self):
        self.driver.get(self.url)

        # Wait for floor list container to load
        floor_list_container = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'floor-vertical-select'))
        )

        # Get all floors using common class pattern
        floors = floor_list_container.find_elements(By.CSS_SELECTOR, "li[role='option']")

        #begin for loop to go through each floor
        for index in range(len(floors)):

            try:
                current_item = floors[index]
                current_item.click()

                # Wait for unit list to load
                unit_list = WebDriverWait(self.driver, 5).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, "ul[data-testid='unit-list']"))
                )
                
                # Get all apartment units
                units = unit_list.find_elements(By.TAG_NAME, 'li')
                
                #begin for loop to go through each apartment unit
                for unit in units:
                    # Extract apartment number text
                    aptnmbr = unit.find_element(By.CSS_SELECTOR, 'button > span > span:first-child').text
                    # Extract only unit ID
                    aptnmbr = re.search(r'\b([A-Za-z]*\d+[A-Za-z-]*)\b', aptnmbr).group(1)
                    # Extract bedroom/bath/sqft info
                    bdrbtr = unit.find_element(By.XPATH, './/div[contains(., "Bed")]').text
                    bed = int(re.search(r'(\d+)\s*Bed', bdrbtr).group(1))
                    bath = int(re.search(r'(\d+)\s*Bath', bdrbtr).group(1))
                    sqft = int(re.search(r'([\d,]+)\s*sq\.\s*ft', bdrbtr).group(1).replace(',', ''))
                    # Extract price/term length
                    details = unit.find_element(By.XPATH, './/span[contains(., "Months")]').text
                    price = int(re.search(r'\$([\d,]+(?:\.\d+)?)', details).group(1).replace(',', ''))
                    term_match = re.search(r"/\s*(\d+)\s*Months", details)
                    term = int(term_match.group(1)) if term_match else None
                    # Extract availability date
                    available = unit.find_element(By.XPATH, './/div[contains(., "Available")]').text

                    self.data.append({
                        "unit_id": aptnmbr,
                        "beds": bed,
                        "baths": bath,
                        "sqft": sqft,
                        "price": price,
                        "term_months": term,
                        "availability": available
                    })


            except Exception as e:
                print("Error:", e)

            finally: 
                sleep(1)
    
    def close(self):
        self.driver.quit()