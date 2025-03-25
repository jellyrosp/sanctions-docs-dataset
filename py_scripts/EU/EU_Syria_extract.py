from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

html_path = "sanctions/EU/Syria/32012R0036_25.11.2024/Consolidated_TEXT_32012R0036_25.11.2024_CLEANED.html"

csv_path = "sanctions/EU/Syria/EU_syria_data.csv"

def format_date(date_str):
    try:
        return datetime.strptime(date_str, "%d.%m.%Y").strftime("%d-%m-%Y")
    except ValueError:
        return "unknown"

def extract_EU_syria_data():

    with open(html_path, "r", encoding="utf-8") as file:
        html_content = file.read()
        soup = BeautifulSoup(html_content, "html.parser")
        table = soup.find("table", class_="borderOj")  
        rows = table.find_all("tr")[1:] if table else []
    
    names = []
    genders = []
    reasons = []
    dates = []

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

    for row in rows:
        cols = row.find_all("td")
        if len(cols) > 1:  
            info_col = cols[2] 
            gender_found = False
            for p_tag in info_col.find_all("p", class_="tbl-norm"):
                text = p_tag.get_text(strip=True).replace(";", "")  
                if "██████" in text:
                    gender_found = True  # Mark it so we don’t add "MISSING"
                    genders.append("unknown")
                    break  
                # Fix cases where "Gender: Male" is on the same line with other info
                if "gender" in text.lower():
                    parts = text.split(";")  
                    for part in parts:
                        if "gender" in part.lower():  # Find the correct segment
                            gender_value = part.split(":", 1)[-1].strip()
                            genders.append(gender_value)
                            gender_found = True
                            break  
            if not gender_found:
                genders.append("unknown")        

    for row in rows:
        cols = row.find_all("td")
        if len(cols) > 1:  
            reason_tags = cols[3].find_all("p", class_="tbl-norm")  # Get all <p> elements inside column 4
            if reason_tags:
                reason_texts = []
                for reason_tag in reason_tags:
                    for img in reason_tag.find_all("img"):
                        img.extract()
                    reason_texts.append(reason_tag.get_text(strip=True))
                reasons.append("; ".join(reason_texts))  # Joining multiple reasons with "; "                

    for row in rows:
        try:
            cols = row.find_all("td")
            if len(cols) <= 4:
                continue
            data_tag = cols[4].find("p", class_="tbl-left")
            if not data_tag:
                dates.append("unknown")
                continue
            for img in data_tag.find_all("img"):
                img.decompose()
            text = data_tag.get_text(strip=True)
            # Normalize missing or placeholder data
            if not text or text.strip() in {"██████", "None", "-", "--"}:
                dates.append("unknown")
            else:
                dates.append(text)
        except Exception as e:
            print(f"Skipping a row due to error: {e}")
            dates.append("unknown")       

    syria_df = pd.DataFrame({
        "Name": names,
        "Gender": genders,
        "Reason": reasons,
        "Dates": dates
    })    

    syria_df["Name"] = syria_df["Name"].str.replace(r"\(\)", "", regex=True).str.strip()
    syria_df["Gender"] = syria_df["Gender"].str.lower().str.strip()
    syria_df.replace({"██████": "unknown",}, inplace=True)
    syria_df = syria_df[~syria_df.apply(lambda row: (row == 'unknown').all(), axis=1)]
    syria_df["Dates"] = syria_df["Dates"].str.strip()
    syria_df["Dates"] = syria_df["Dates"].apply(format_date) 


    #print(len(names), len(genders), len(reasons), len(dates))
    print(syria_df.info())
    #return syria_df.to_csv(csv_path, index=False)


extract_EU_syria_data()

