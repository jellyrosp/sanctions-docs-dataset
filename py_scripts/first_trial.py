from bs4 import BeautifulSoup
import pandas as pd

# Load the HTML file
html_path = "sanctions/EU/Syria/Consolidated_TEXT_32012R0036_25.11.2024/Consolidated_TEXT_32012R0036_25.11.2024_CLEANED.html"

with open(html_path, "r", encoding="utf-8") as file:
    html_content = file.read()

# Parse HTML with BeautifulSoup
soup = BeautifulSoup(html_content, "html.parser")

# Find the main sanctions table
table = soup.find("table", class_="borderOj")  # Adjust class name if needed

# Extract all rows (skip header row)
rows = table.find_all("tr")[1:] if table else []

# Extract names from the second column (index 1)
names = []

for row in rows:
    cols = row.find_all("td")
    if len(cols) > 1:  # Ensure there are enough columns
        name_tag = cols[1].find("p", class_="tbl-norm")  # Get <p> inside the Name column
        if name_tag:
            # Remove images inside the <p> tag
            for img in name_tag.find_all("img"):
                img.extract()
            # Extract cleaned name
            names.append(name_tag.get_text(strip=True))


genders = []

for row in rows:
    cols = row.find_all("td")
    if len(cols) > 2:  # Ensure there are enough columns
        info_col = cols[2]  # The third column contains identifying information
        gender_found = False

        for p_tag in info_col.find_all("p", class_="tbl-norm"):
            text = p_tag.get_text(strip=True).replace(";", "")  

            # Check if the row has anonymized data (██████), skip it
            if "██████" in text:
                gender_found = True  # Mark it so we don’t add "MISSING"
                genders.append("REDACTED")
                break  # Skip further processing for this row

            # Fix cases where "Gender: Male" is on the same line with other info
            if "gender" in text.lower():
                parts = text.split(";")  # Split on semicolons (common separator)
                for part in parts:
                    if "gender" in part.lower():  # Find the correct segment
                        gender_value = part.split(":", 1)[-1].strip()
                        genders.append(gender_value)
                        gender_found = True
                        break  # Stop searching after finding gender

        # If no gender found, explicitly mark as "MISSING"
        if not gender_found:
            genders.append("MISSING")





reasons = []

for row in rows:
    cols = row.find_all("td")
    if len(cols) > 3:  # Ensure there are enough columns
        reason_tag = cols[3].find("p", class_="tbl-norm")  # Get <p> inside the Name column
        if reason_tag:
            # Remove images inside the <p> tag
            for img in reason_tag.find_all("img"):
                img.extract()
            # Extract cleaned name
            reasons.append(reason_tag.get_text(strip=True))




# dates = []

# for row in rows:
#     cols = row.find_all("td")
#     if len(cols) > 4:  # Ensure there are enough columns
#         data_tag = cols[4].find("p", class_="tbl-left")  # Get <p> inside the Name column
#         if data_tag:
#             # Remove images inside the <p> tag
#             for img in data_tag.find_all("img"):
#                 img.extract()
#             # Extract cleaned name
#             dates.append(data_tag.get_text(strip=True))

#print(dates)

dates = []

for row in rows:
    try:
        cols = row.find_all("td")
        if len(cols) <= 4:
            continue

        data_tag = cols[4].find("p", class_="tbl-left")
        if not data_tag:
            dates.append("MISSING")
            continue

        # Remove any <img> tags inside the <p>
        for img in data_tag.find_all("img"):
            img.decompose()

        text = data_tag.get_text(strip=True)

        # Normalize missing or placeholder data
        if not text or text.strip() in {"██████", "None", "-", "--"}:
            dates.append("MISSING")
        else:
            dates.append(text)

    except Exception as e:
        print(f"Skipping a row due to error: {e}")
        dates.append("MISSING")


syria_df = pd.DataFrame({
    "Name": names,
    "Gender": genders,
    "Reason": reasons,
    "Dates": dates
})

#print(dates)
syria_df["Name"] = syria_df["Name"].str.replace(r"\(\)", "", regex=True).str.strip()
syria_df["Gender"] = syria_df["Gender"].str.lower().str.strip()
syria_df.replace({"██████": "REDACTED", "MISSING": "UNKNOWN"}, inplace=True)
syria_df["Dates"] = syria_df["Dates"].str.strip()

syria_df.to_csv("sanctions/EU/Syria/Consolidated_TEXT_32012R0036_25.11.2024/syria_data.csv", index=False)
