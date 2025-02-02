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
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
import psutil

MAX_QUERIES = 60



# Lock for thread-safe CSV writing
csv_lock = Lock()

def click_element(driver, element):
    """Wait for an element to be clickable, click it, and wait for the Reviews tab to appear."""
    try:
        
        driver.execute_script("arguments[0].scrollIntoView();", element)
        time.sleep(1) 
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable(element)).click()
        time.sleep(1)  # Allow details to load
    except Exception as e:
        print(f"Error while clicking element or waiting for Reviews tab: ")

def click_element_js(driver, element):
    """Click an element using JavaScript to bypass overlays."""
    try:
        # driver.execute_script("arguments[0].scrollIntoView();", element)
        
        driver.execute_script("arguments[0].click();", element)
    except Exception as e:
        print(f"JavaScript click failed: ")





# Key modifications to improve thread safety and element reliability

# 1. Add these imports at the top

# 2. Modify thread monitoring with resource awareness

    # Rest of original monitor_and_restart_threads implementation
    # ... use max_threads instead of num_threads ...


# 3. Enhanced handle_reviews with better error recovery
def handle_reviews(driver):
    latest_review_date = "No review date"
    max_retries = 3
    retry_delay = 1.5  # Increased delay between retries
    
    try:
        # Phase 1: Ensure reviews tab is open
        # for attempt in range(max_retries+1):
            # try:
            #     review_buttons =WebDriverWait(driver, 8).until(
            #         EC.element_to_be_clickable((By.XPATH,  "//div[contains(@aria-label, 'Reviews')]"))
            #     )
                
            #     break
            # except (TimeoutException, StaleElementReferenceException):
            #     if attempt == max_retries:
            #         raise
            #     print(f"Retrying reviews tab open ({attempt+1}/{max_retries})")
        review_buttons = driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Reviews')]")
        
        review_buttons.click()
                # time.sleep(retry_delay * (attempt+1))

        # Phase 2: Sorting interaction with hybrid waits
        sorting_success = False
        for attempt in range(max_retries+1):
            try:
                
                
                # Get fresh sort button reference
                sort_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, 
                        "//button[contains(@aria-label, 'Sort reviews') or contains(@aria-label, 'Most relevant')]"))
                )
                
                # Scroll and click with visual verification
                # driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", sort_button)
                time.sleep(0.5)  # Allow for smooth scrolling
                sort_button.click()
                
                # # Wait for menu animation
                # WebDriverWait(driver, 10).until(
                #     EC.visibility_of_element_located((By.XPATH, "//div[@role='menu'][@aria-hidden='false']"))
                # )
                sorting_success = True
                break
                
            except Exception as e:
                print(f"Sorting attempt {attempt+1} failed:")
                if attempt == max_retries:
                    raise
                time.sleep(retry_delay * (attempt+1))

        if not sorting_success:
            return latest_review_date

        # Phase 3: Select newest with multiple fallback strategies
        newest_selectors = [
            "//div[contains(text(), 'Newest')]",  # Primary selector
            "//div[contains(@class, 'fontBodyMedium') and contains(text(), 'Newest')]",  # Fallback 1
            "//div[@role='menuitemradio' and contains(.//text(), 'Newest')]"  # Fallback 2
        ]
        
        for selector in newest_selectors:
            try:
                time.sleep(0.5)  
                newest_option = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                driver.execute_script("arguments[0].click();", newest_option)
                break
            except Exception as e:
                print(f"Newest selector failed: {selector} - {str(e)}")
        else:
            print("All newest selectors failed")
            return latest_review_date

        # Phase 4: Wait for review list stabilization
        WebDriverWait(driver, 15).until(
            lambda d: d.find_element(By.XPATH, 
                "//div[contains(@class, 'jJc9Ad')][1]//span[contains(@class, 'rsqaWe') or contains(@class, 'xRkPPb')]")
        )

        # Phase 5: Date extraction with multiple fallbacks
        date_selectors = [
            "//span[contains(@class, 'rsqaWe') or contains(@class, 'xRkPPb')][1]",  # Primary
            "//div[contains(text(), 'ago')][1]",  # Relative time
            
        ]
        
        for selector in date_selectors:
            try:
                date_element = WebDriverWait(driver, 3).until(
                    EC.visibility_of_element_located((By.XPATH, selector))
                )
                latest_review_date = date_element.text.strip()
                break
            except Exception as e:
                print(f"Date selector failed: {selector} - {str(e)}")

    except Exception as e:
        print(f"Critical review handling failure: {str(e)}")
    
    return latest_review_date















def scrape_google_maps(search_query, result_queue):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--enable-gpu")  # Enable GPU acceleration
    # chrome_options.add_argument("--ignore-gpu-blacklist")  # Ignore GPU blocklist to for
    # chrome_options.add_argument("--headless")

    # """Scrape Google Maps for a single query and store results in a thread-safe queue."""
    # options = webdriver.ChromeOptions()
    chrome_options.add_argument('--start-maximized')
    driver = webdriver.Chrome(service=Service("C:\chromedriver-win64\chromedriver.exe"), options=chrome_options)

    business_type, search_query = ast.literal_eval(search_query)
    visited_names = set()

    try:
        driver.get("https://www.google.com/maps")
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "searchboxinput")))
        
        search_box = driver.find_element(By.ID, "searchboxinput")
        search_box.send_keys(search_query)
        search_box.send_keys(Keys.ENTER)

        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, "Nv2PK")))
        actions = ActionChains(driver)
        businesses = []
        count = 0

        prev_count = 0
        no_change_count = 0  # Track how many times results remain unchanged

        while True:
            actions.send_keys(Keys.PAGE_DOWN).perform()
            time.sleep(2)  # Allow time for new results to load

            results = driver.find_elements(By.CLASS_NAME, "Nv2PK")
            current_count = len(results)

            if current_count == prev_count:
                no_change_count += 1
            else:
                no_change_count = 0  # Reset counter if new results appear

            if no_change_count >= 2:  # If no new results appear after 3 scrolls, stop
                print("No new results found after scrolling. Ending search.")
                break

            prev_count = current_count

            if count >= MAX_QUERIES:
                print("Reached maximum limit of queries. Stopping search.")
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
                    button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(@aria-label, 'Reviews')]")))
                    if not button:
                        print("<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>")
                        continue
                        
                    
                    

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
                        print("Couldnt find Category")
                    
                    if category == "No category":
                        try:
                            category_div =driver.find_element(By.XPATH, "//button[contains(@class, 'DkEaL')]")
                            if category_div:
                                category = category_div.text.strip()
                        except:
                            print("Couldnt find Category")
                    
                    
                    
                    

                    # Extract website
                    
                    website_div = detail_soup.find('div', class_='rogA2c ITvuef')
                    if website_div:
                        website_inner_div = website_div.find('div')
                        if website_inner_div:
                            website = website_inner_div.text.strip()
                    
                    
                        if website=='No website':
                            try:
                                site = driver.find_element(By.XPATH, 
                                    "//div[contains(@class, 'Io6YTe') and contains(@class, 'fontBodyMedium') and "
                                    "(contains(text(), '.gov') or contains(text(), '.org') or contains(text(), '.edu') or contains(text(), '.com') or contains(text(), '.net'))]"
                                    )
                                if site:
                                    website = site.text.strip() 
                            except:
                                print('Error in finding Second Website Method')
                                
                                
                    latest_review_date = handle_reviews(driver)                        
                                
                    # try:
                    #     review_buttons = WebDriverWait(driver, 10).until(
                    #         EC.element_to_be_clickable((By.XPATH, "//button[contains(@aria-label, 'Reviews')]"))
                    #     )
                    #     review_buttons.click()
                    #     if not review_buttons:
                    #         print("Reviews tab not found. Skipping sorting and directly extracting latest review date.")
                    #         raise Exception("Reviews tab not found")
                    # except Exception as e:
                    #     print("Error while switching to the reviews tab:",)
                    #     continue

                    # # # Extract the latest review date, whether or not the Reviews tab appeared

                    # # Click the sort button (Most Relevant) and select "Newest"
                    # try:
                    #     time.sleep(2) 
                    #     # Try finding the standard "Sort" button
                    #     sort_button_xpath = "//button[contains(@aria-label, 'Sort reviews')]"
                    #     most_relevant_button_xpath = "//button[contains(@aria-label, 'Most relevant')]"

                    #     try:
                    #         sort_button = WebDriverWait(driver, 2).until(
                    #             EC.element_to_be_clickable((By.XPATH, sort_button_xpath))
                    #         )
                    #     except:
                    #         sort_button = None  # If not found, proceed to check for "Most relevant"

                    #     if not sort_button:
                    #         try:
                    #             sort_button = WebDriverWait(driver, 2).until(
                    #                 EC.element_to_be_clickable((By.XPATH, most_relevant_button_xpath))
                    #             )
                    #         except:
                    #             print("Neither 'Sort' nor 'Most relevant' button found. Skipping sorting.")
                    #             raise Exception("Sorting button not found.")
                        
                    #     # Click the found sorting button
                    #     click_element_js(driver, sort_button)
                        

                    #     # Wait for the "Newest" option to appear and click it
                    #     newest_option = WebDriverWait(driver, 10).until(
                    #         EC.presence_of_element_located((By.XPATH, "//div[text()='Newest']"))
                    #     )
                    #     click_element_js(driver, newest_option)
                    #     # Allow the reviews section to update

                    #     # print("Sorting reviews by 'Newest' successfully.")
                    # except Exception as e:
                    #     print(f"Sorting option not found or could not be clicked: ")
                    #     continue


                    # latest_review_date = "No review date"
                    # try:
                    #     latest_review_element = WebDriverWait(driver, 2).until(
                    #         EC.presence_of_element_located((By.XPATH, "//span[@class='xRkPPb'][1]"))
                    #     )
                    #     latest_review_date = latest_review_element.text.strip()
                    # except Exception as e:
                    #     print("No review date found:")
                    
                    # if latest_review_date = "No review date"
                    #     try:
                    #         latest_review_element = WebDriverWait(driver, 1).until(
                    #             EC.presence_of_element_located((By.XPATH, "//span[@class='rsqaWe'][1]"))
                    #         )
                    #         latest_review_date = latest_review_element.text.strip()
                    #     except Exception as e:
                    #         print("No review date found:")    

                    # # Extract the latest review date after sorting reviews by "Newest"
                    # latest_review_date = "No review date"

                    # try:
                    #     time.sleep(1)
                    #     # Wait for the latest review date element to appear
                    #     WebDriverWait(driver, 10).until(
                    #         EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'ago')]"))
                    #     )
                    #     # Allow reviews to load properly

                    #     # Check both possible review date formats
                    #     try:
                            
                    #         latest_review_element = driver.find_element(By.XPATH, "//span[contains(text(), 'ago')][1]")
                    #         latest_review_date = latest_review_element.text.strip()
                    #     except Exception as e:
                    #         print("First review date element (xRkPPb) not found:", )

                        # if latest_review_date == "No review date":
                        #     try:
                        #         latest_review_element = driver.find_element(By.XPATH, "//span[contains(@class, 'rsqaWe')][1]")
                        #         latest_review_date = latest_review_element.text.strip()
                        #     except Exception as e:
                        #         print("Second review date element (rsqaWe) not found:", e)

                    # except Exception as e:
                    #     print("Error while extracting latest review date:", )

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
                    print("")

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


def monitor_and_restart_threads(queries, output_file, max_threads=None):
    """Dynamically adjust threads based on system resources"""
    result_queue = Queue()
    if not max_threads:
        # Calculate safe thread count based on CPU and memory
        cpu_count = psutil.cpu_count(logical=False)
        mem_available = psutil.virtual_memory().available >> 30  # GB
        max_threads = min(cpu_count, max(1, mem_available//2))
        print(f"Auto-configured to {max_threads} threads based on system resources")
    
    threads = []
    active_threads = set()  # Track active threads
    
    def create_thread(thread_queries):
        thread = threading.Thread(target=process_queries, args=(thread_queries, result_queue, output_file), daemon=True)
        active_threads.add(thread)  # Add to active tracking
        return thread
    

    # Start threads initially
    for i in range(max_threads):
        thread_queries = queries[i::max_threads]  
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
    import multiprocessing

    # Auto-configure threads based on system resources
    physical_cores = multiprocessing.cpu_count()
    mem = psutil.virtual_memory().available / (1024 ** 3)  # GB
    safe_threads = min(physical_cores, int(mem // 2.5))  # 2.5GB per thread
    safe_threads = max(1, safe_threads - 1)  # Leave one core free
    
    print(f"System resources: {physical_cores} cores, {mem:.1f}GB RAM")
    print(f"Starting with {safe_threads} safe threads")

    monitor_and_restart_threads(queries, output_file, max_threads=safe_threads)