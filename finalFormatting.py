import pandas as pd

# Open the CSV file
file_path = 'LeadsApart.csv'  # Replace with your actual file path
df = pd.read_csv(file_path)

# Specify column names
columns = [
    "Type of Business", "Sub-Category", "Name of Business", "Website",
    "# of Reviews", "Rating", "Latest Review Date", "Business Address", "Phone Number"
]

# Drop rows with unwanted values
df = df[df["# of Reviews"] != 'No reviews']
df = df[df["Rating"] != 'No ratings']
df = df[df["Latest Review Date"] != 'No review date']
df = df[df["Phone Number"] != 'No phone number']
df = df[df["Business Address"] != 'No address']
df = df[df["Website"] != 'No website']

# Clean and convert numeric columns
df["# of Reviews"] = df["# of Reviews"].str.replace(',', '').astype(int)

# Remove "on Google" from 'Latest Review Date'
df["Latest Review Date"] = df["Latest Review Date"].str.replace(r'on\s*\n*Google', '', regex=True)

# Drop addresses without a comma
df = df[df["Business Address"].str.contains(",", na=False)]

# Keep rows where '# of Reviews' is at least 4
df = df[df["# of Reviews"] >= 4]

# Remove duplicate rows based on 'Phone Number'
df = df.drop_duplicates(subset=["Phone Number"], keep='first')

# Filter based on city names
city_names = "Lake Worth, Florida, Boynton Beach, 33411, 33444, 33431"  
city_list = [city.strip() for city in city_names.split(',')]
df = df[df["Business Address"].astype(str).str.contains('|'.join(city_list), case=False, na=False)]

# **Sort by the first column**
df = df.sort_values(by=columns[0], ascending=True)

# Save to Excel with custom column widths
output_file = 'ff.xlsx'
with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
    df.to_excel(writer, index=False, sheet_name='Sheet1')

    # Get workbook and worksheet
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']

    # **Define custom column widths**  
    column_widths = {
        "Type of Business": 20,
        "Sub-Category": 18,
        "Name of Business": 30,
        "Website": 35,
        "# of Reviews": 12,
        "Rating": 10,
        "Latest Review Date": 20,
        "Business Address": 50,
        "Phone Number": 15
    }

    # Apply custom widths
    for i, col in enumerate(columns):
        width = column_widths.get(col, 15)  # Default width if not specified
        worksheet.set_column(i, i, width)

print(f"File '{output_file}' saved successfully with custom column widths! ✅")
