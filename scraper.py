from selenium import webdriver 
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import csv
from threading import Thread
from queue import Queue
from threading import Lock
import threading
import ast
import time

MAX_QUERIES = 10

# Lock for thread-safe CSV writing
csv_lock = Lock()

def click_element(driver, element):
    """Wait for an element to be clickable, click it, and wait for the Reviews tab to appear."""
    try:
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable(element))
        driver.execute_script("arguments[0].scrollIntoView();", element)
        element.click()

        # Wait for the "Reviews" tab to appear (specific div with class "Gpq6kf fontTitleSmall" and text "Reviews")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[contains(@class, 'Gpq6kf') and contains(@class, 'fontTitleSmall') and contains(text(), 'Reviews')]")
            )
        )

    except Exception as e:
        print(f"Error while clicking element or waiting for Reviews tab: {e}")

def click_element_js(driver, element):
    """Click an element using JavaScript to bypass overlays."""
    try:
        driver.execute_script("arguments[0].scrollIntoView();", element)
        driver.execute_script("arguments[0].click();", element)
    except Exception as e:
        print(f"JavaScript click failed: {e}")

def scrape_google_maps(search_query, result_queue):
    """Scrape Google Maps for a single query and store results in a thread-safe queue."""
    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')
    driver = webdriver.Chrome(service=Service("C:\chromedriver-win64\chromedriver.exe"), options=options)

    business_type, search_query = ast.literal_eval(search_query)
    visited_names = set()

    try:
        driver.get("https://www.google.com/maps")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "searchboxinput")))
        
        search_box = driver.find_element(By.ID, "searchboxinput")
        search_box.send_keys(search_query)
        search_box.send_keys(Keys.ENTER)

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "Nv2PK")))
        actions = ActionChains(driver)
        businesses = []
        count = 0

        while True:
            actions.send_keys(Keys.PAGE_DOWN).perform()
            WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, "Nv2PK")))

            try:
                driver.find_element(By.XPATH, "//span[contains(@class, 'HlvSq') and contains(text(), 'reached')]")
                print("End of list reached, stopping the scrape.")
                break
            except:
                pass
            
            if count >= MAX_QUERIES:
                print("End of list reached by LIMIT, stopping the scrape.")
                break

            results = driver.find_elements(By.CLASS_NAME, "Nv2PK")
            for result in results:
                try:
                    rating = "No rating"
                    address = "No address"
                    phone = "No phone number"
                    category = "No category"
                    website = "No website"
                    latest_review_date = "No review date"
                    reviews = "No reviews"

                    name_element = result.find_element(By.CLASS_NAME, "qBF1Pd")
                    name = name_element.text if name_element else "No name"
                    if name in visited_names:
                        continue


                    
                    if(count>=MAX_QUERIES):
                        break
                    count+=1
                    visited_names.add(name)
                    click_element(driver, result)
                    

                    detail_soup = BeautifulSoup(driver.page_source, 'html.parser')
                    # Extract review count and rating
                    try:
                        review_element = result.find_element(By.CLASS_NAME, "UY7F9")
                        reviews = review_element.text if review_element else "No reviews"
                    except:
                        reviews = "No reviews"

                    try:
                        rating_element = result.find_element(By.CLASS_NAME, "MW4etd")
                        rating = rating_element.text if rating_element else "No ratings"
                    except:
                        rating = "No ratings"

                    reviews = reviews.replace('(', '').replace(')', '')



                    # Extract address
                    
                    address_element = detail_soup.find('div', class_='Io6YTe')
                    if address_element:
                        address = address_element.text.strip()
                        
                    if address=='No address':
                        address_element=driver.find_element(By.XPATH, 
                            "//div[contains(@class, 'Io6YTe ') and contains(@class, 'fontBodyMedium ') and contains(text(), 'United')]")
                        if address_element:
                            address = address_element.text.strip()

                    # Extract phone number
                    phone_elements = detail_soup.find_all('div', class_='Io6YTe')
                    for div in phone_elements:
                        if div.text.startswith('+') or div.text.replace('-', '').isdigit():
                            phone = div.text.strip()
                            break
                    
                    if phone=='No phone number':
                        phone_element=driver.find_element(By.XPATH, 
                            "//div[contains(@class, 'Io6YTe ') and contains(@class, 'fontBodyMedium ') and contains(text(), '+1')]")
                        if phone_element:
                            phone = phone_element.text.strip()    

                    # Extract category (Primary Method)
                    try:
                        category_div = detail_soup.find('button', class_='DkEaL')
                        if category_div:
                            category = category_div.text.strip()
                    except:
                        category = "No category"
                    
                    
                    # if category == "No category":
                    #     parent_span = driver.find_element(By.XPATH, "//span[contains(@class, 'mgr77e')]")
                    #     # Find all child span elements inside the parent
                    #     child_spans = parent_span.find_elements(By.TAG_NAME, 'span')
                    #     # Filter out the span that has meaningful text (not just a dot '.')
                    #     for span in child_spans:
                    #         text = span.text.strip()
                    #         if text and text != ".":
                    #             print("Text found:", text)  # Print the text of the span
                    #             category=text
                    #             break  # Exit after finding the span with meaningful text    


                    # Extract website
                    
                    website_div = detail_soup.find('div', class_='rogA2c ITvuef')
                    if website_div:
                        website_inner_div = website_div.find('div')
                        if website_inner_div:
                            website = website_inner_div.text.strip()
                    try:
                        if website=='No website':
                            site = driver.find_element(By.XPATH, 
                                "//div[contains(@class, 'Io6YTe') and contains(@class, 'fontBodyMedium') and "
                                "(contains(text(), '.gov') or contains(text(), '.org') or contains(text(), '.edu') or contains(text(), '.com') or contains(text(), '.net'))]"
    )
                            if site:
                                website = site.text.strip() 
                    except:
                        print('Error in finding Website')            

                    

                    
                    # Alternative category extraction if primary method fails
                    


                    
                    
                    try:
                        review_dates = detail_soup.find_all('span', class_='rsqaWe')
                        if review_dates:
                            latest_review_date = review_dates[0].text.strip()
                        else:
                            print("No review date found(Its a motel or hotel)")
                    except Exception as e:
                        print("EXCEPTION>>>No review date found(Its a motel or hotel)")
                        
                    if latest_review_date=='No review date':
                        WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located(
                        (By.XPATH, "//div[contains(@class, 'Gpq6kf') and contains(@class, 'fontTitleSmall') and contains(text(), 'Reviews')]")
                        )
                        )
                        try:
                            review_buttons = driver.find_elements(By.XPATH, "//div[contains(@class, 'Gpq6kf') and contains(@class, 'fontTitleSmall') and contains(text(), 'Reviews')]")
                            if review_buttons:  
                                click_element_js(driver, review_buttons[0])  # Click the first Reviews button
                                time.sleep(1)  # Wait for the reviews to load
                            else:
                                print("Could not find the reviews tab.Failed in finding Review Button")
                        except Exception as e:
                            print("Error while switching to the reviews tab:", e)

                        # Click the sort button (Most Relevant) and select "Newest"
                        try:
                            sort_button = WebDriverWait(driver, 5).until(
                                EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Most relevant']"))
                            )
                            click_element_js(driver, sort_button)  # Click the sorting button

                            # Click "Newest" option
                            newest_option = WebDriverWait(driver, 5).until(
                                EC.element_to_be_clickable((By.XPATH, "//div[text()='Newest']"))
                            )
                            click_element_js(driver, newest_option)
                            time.sleep(1)  # Wait briefly for sorting to take effect
                        except Exception as e:
                            print("Sorting option not found:", e)

                        # Wait for the latest review date to appear
                        latest_review_date = "No review date"
                        try:
                            latest_review_element = WebDriverWait(driver, 5).until(
                                EC.presence_of_element_located((By.XPATH, "//span[@class='xRkPPb'][1]"))
                            )
                            latest_review_date = latest_review_element.text.strip()
                        except Exception as e:
                            print("No review date found:", e)

           
                    businesses.append({
                        'Type of Business': business_type,
                        'Sub-Category': category,
                        'Name of Business': name,
                        'Website': website,
                        '# of Reviews': reviews,
                        'Rating': rating,
                        'Latest Review Date': latest_review_date,
                        'Business Address': address,
                        'Phone Number': phone
                    })
                except Exception as e:
                    print(f"Error extracting details for a business: {e}")

        result_queue.put(businesses)

    finally:
        driver.quit()

def save_to_csv(data, filename):
    """Save scraped data to a CSV file."""
    with csv_lock:
        with open(filename, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=['Type of Business', 'Sub-Category', 'Name of Business', 'Website',
                                                      '# of Reviews', 'Rating', 'Latest Review Date',
                                                      'Business Address', 'Phone Number'])
            if file.tell() == 0:
                writer.writeheader()
            writer.writerows(data)

def process_queries(queries, result_queue, output_file):
    """Process a batch of queries."""
    for query in queries:
        print(f"Scraping data for query: {query}")
        scrape_google_maps(query, result_queue)

        while not result_queue.empty():
            results = result_queue.get()
            save_to_csv(results, output_file)

def monitor_and_restart_threads(queries, output_file, num_threads):
    """Monitors threads and restarts them if they die, but exits when all queries are processed."""
    result_queue = Queue()
    threads = []
    active_threads = set()  # Track active threads
    
    def create_thread(thread_queries):
        thread = threading.Thread(target=process_queries, args=(thread_queries, result_queue, output_file), daemon=True)
        active_threads.add(thread)  # Add to active tracking
        return thread
    
    # Start threads initially
    for i in range(num_threads):
        thread_queries = queries[i::num_threads]  
        thread = create_thread(thread_queries)
        threads.append(thread)
        thread.start()
    
    # Monitor threads and restart only if needed
    while active_threads:
        for thread in list(active_threads):  
            if not thread.is_alive():  # Remove finished threads
                active_threads.remove(thread)
        time.sleep(2)  # Reduce CPU usage
    
    print("All queries processed. Exiting.")

if __name__ == "__main__":
    input_file = "queries.txt"
    output_file = "LeadsApart.csv"

    with open(input_file, mode='r', encoding='utf-8') as file:
        queries = [line.strip() for line in file if line.strip()]

    monitor_and_restart_threads(queries, output_file, num_threads=1)