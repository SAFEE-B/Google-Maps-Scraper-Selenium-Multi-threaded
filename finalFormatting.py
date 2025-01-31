import pandas as pd

# Open the CSV file
file_path = 'LeadsApart.csv'  # Replace with your file path
df = pd.read_csv(file_path)

# Specify the column to check
column_name1 = '# of Reviews'  # Replace with the name of the column you're checking

# Drop rows where the specified column has 'No reviews'
df = df[df[column_name1] != 'No reviews']

# # Remove commas and convert the column to integers
df[column_name1] = df[column_name1].str.replace(',','')
df[column_name1] = df[column_name1].astype(int)

column_name2 = 'Rating'  # Replace with the name of the column you're checking

# Drop rows where the specified column has 'No ratings'
df = df[df[column_name2] != 'No ratings']

column_name3 = 'Latest Review Date'  # Replace with the name of the column you're checking

# Drop rows where the specified column has 'No review date'
df = df[df[column_name3] != 'No review date']
# Drop rows where the specified column has 'No review date'
df[column_name3]=df[column_name3].str.replace(r'on\s*\n*Google', '', regex=True)

column_name4 = 'Phone Number'  # Replace with the name of the column you're checking

# Drop rows where the specified column has 'No phone number'
df = df[df[column_name4] != 'No phone number']

column_name5 = 'Business Address'  # Replace with the name of the column you're checking

# Drop rows where the specified column has 'No address'
df = df[df[column_name5] != 'No address']

# Drop rows where the address does not contain a comma
df = df[df[column_name5].str.contains(",", na=False)]

column_name6 = 'Website'  # Replace with the name of the column you're checking

# Drop rows where the specified column has 'No website'
df = df[df[column_name6] != 'No website']

# Keep rows where '# of Reviews' is greater than or equal to 4
df = df[df[column_name1] >= 4]

# Remove duplicate rows based on the 'Phone Number' column
df = df.drop_duplicates(subset=['Phone Number'], keep='first')

city_names = "Lake worth, Florida, Boynton Beach, 33411, 33444, 33431"  # Replace with actual city names
# Ensure city names are properly formatted
print(df)
city_list = [city.strip() for city in city_names.split(',')]  # Trim any extra spaces

# Drop rows where the address doesn't contain any of the cities
df = df[df['Business Address'].astype(str).str.contains('|'.join(city_list), case=False, na=False)]
print(df)


# Optionally, save the cleaned dataframe back to an Excel file
df.to_excel('final1.xlsx', index=False)

# Display the cleaned dataframe
print(df)
