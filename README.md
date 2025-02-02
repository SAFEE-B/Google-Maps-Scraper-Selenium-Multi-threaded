# Free Google Maps Scraper for Lead Generation (Using Selenium)

## Overview
This Google Maps scraper is designed for lead generation, using Selenium for automation. It extracts business details from Google Maps based on provided search queries and saves the results in a CSV file.

### **Fields Returned:**
- **Business Type**
- **Sub Category**
- **Name**
- **Phone Number**
- **Website**
- **Address**
- **Rating**
- **Total Reviews**
- **Latest Review Date**

## **How to Run**
1. **Prepare Queries**
   - Use the prompt provided below to generate search queries.
   - Save these queries in a file named `queries.txt`.

2. **Run the Scraper**
   - Execute the script to start scraping.
   - The scraper continuously adds data to the CSV file.
   - If you decide to stop scraping mid-way, you can safely terminate the terminal session; all data collected up to that point will be saved.

3. **Adjust Scraper Settings**
   - The `Max_queries` variable in the code determines how many businesses are fetched per query. Adjust this as needed.
   - The scraper is **multithreaded**, meaning it runs multiple Selenium browser windows simultaneously.
   - To modify the number of threads, change the relevant parameter in the code (not the default value).
   - Recommended settings (based on a test system with **32GB RAM, Ryzen 5800H, and 10Mbps Internet**): **6 to 8 threads**.

4. **Format the Data**
   - After scraping, run the `FinalFormatter` script to clean and structure the data for better readability and usability. 

## **Generating Search Queries(Prompt to LLM)**


I need a list of search queries for a Google Maps scraper. Given a list of business types and a general location, generate at least **200 unique search queries** by combining each business type with **specific locations** inside the provided area.  

### **Instructions:**  
1. **Use every business type** in the provided list (e.g., `"Apartment buildings, motels, trailer parks"`).  
2. **Generate location-based queries** by combining each business type with:  
   - **Major cities or towns** in the specified region.  
   - **Suburbs and smaller towns** around the major cities.  
   - **Well-known neighborhoods, districts, and residential areas** inside the cities.  
   - **Popular commercial areas, landmarks, or business hubs** (e.g., `"Downtown, Uptown, Financial District"`).  
3. **Ensure a minimum of 200 queries** by diversifying the combinations and maximizing geographic coverage.  
4. **Format each query as:**  
   - `[Business Type], [Search Query]`  
   - Example: `"Hotels", "Hotels in Downtown, Minneapolis, MN"`  
5. **Maintain uniqueness**: Avoid duplicates and ensure all locations are inside the specified region.  

### **Example Input:**  
**Business types:** Apartment buildings, motels, trailer parks  
**Location:** St. Louis, Roseville, Minnesota  

### **Example Output Format:**  
```
"Hotels", "Hotels near Roseville, MN"  
"Hotels", "Hotels near Minneapolis, MN"  
"Hotels", "Hotels near St. Louis Park, MN"  
"Hotels", "Hotels near St. Paul, MN"  
"Motels", "Motels near Downtown, Minneapolis, MN"  
"Motels", "Motels near Mall of America, Bloomington, MN"  
"Trailer parks", "Trailer parks near Eagan, MN"  
"Trailer parks", "Trailer parks near Como Park, St. Paul, MN"  
```
  
Now, generate a **similar list of at least 200 queries** for the following:  
**([GIVE YOU BUSINESS TYPES] + [GIVE YOUR CITIES/LOCATIONS])**  

Ensure that **all query locations are within the given areas or cities.**

---

This scraper provides an efficient way to gather business leads from Google Maps with automation and multithreading. Adjust the settings based on your hardware capabilities to optimize performance.
