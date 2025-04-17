from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

html_path = "sanctions/EU/Russia/Russia_jointed_TEXT.html"

csv_path = "sanctions/EU/Russia/EU_russia_data1.csv"

def format_date(date_str):
    try:
        return datetime.strptime(date_str, "%d.%m.%Y").strftime("%d-%m-%Y")
    except ValueError:
        return "unknown"

def extract_EU_russia_data():

    with open(html_path, "r", encoding="utf-8") as file:
        html_content = file.read()
        soup = BeautifulSoup(html_content, "html.parser")
        tables = soup.find_all("table")
    
    names = []
    genders = []
    reasons = []
    dates = []
    doc_title = []
    doc_number = []
    doc_url = []
    case_study = []
    nationality = [] 


    for table in tables:
        table_class = table.get("class", [])
        rows = table.find_all("tr")[1:]  # Skip header row

        for row in rows:
            cols = row.find_all("td")
            if len(cols) > 1:
                name_tag = cols[1].find("p", class_="tbl-norm")
                if name_tag:
                    names.append(name_tag.get_text(strip=True))
                    if table_class and table_class[0] == "borderOj":
                        doc_title.append("COUNCIL_REGULATION _EU_ 2024_1485_27_May_2024")
                        doc_number.append("02024R1485-20240913")
                        doc_url.append("http://data.europa.eu/eli/reg/2024/1485/2024-09-13")
                    else:
                        doc_title.append("COUNCIL_REGULATION_EU_2024_2642_8_October_2024")
                        doc_number.append("02024R2642-20241216")
                        doc_url.append("http://data.europa.eu/eli/reg/2024/2642/2024-12-16")
                    case_study.append("Russia")
    
        for row in rows:
            cols = row.find_all("td")
            if len(cols) > 1:  
                info_col = cols[2] 
                gender_found = False
                nat_found = False
                for p_tag in info_col.find_all("p", class_="tbl-norm"):
                    text = p_tag.get_text(strip=True).replace(";", "")  
                    if "gender" in text.lower():
                        parts = text.split(";")  
                        for part in parts:
                            if "gender" in part.lower():  
                                gender_value = part.split(":", 1)[-1].strip()
                                genders.append(gender_value)
                                gender_found = True
                                break 
                    if "nationality" in text.lower():  
                        parts = text.split(";")  
                        for part in parts:
                            if "nationality" in part.lower():  # ✅ Same typo fixed
                                nat_value = part.split(":", 1)[-1].strip()
                                nationality.append(nat_value)
                                nat_found = True
                                break              
                if not gender_found:
                    genders.append("unknown") 
                if not nat_found:
                    nationality.append("unknown") 
       

        for row in rows:
            cols = row.find_all("td")
            if len(cols) > 1:  
                reason_tags = cols[3].find_all("p", class_="tbl-norm")  
                if reason_tags:
                    reason_texts = []
                    for reason_tag in reason_tags:
                        for img in reason_tag.find_all("img"):
                            img.extract()
                        reason_texts.append(reason_tag.get_text(strip=True))
                    reasons.append("; ".join(reason_texts)) 

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
                if not text or text.strip() in {"██████", "None", "-", "--"}:
                    dates.append("unknown")
                else:
                    dates.append(text)
            except Exception as e:
                print(f"Skipping a row due to error: {e}")
                dates.append("unknown")       

    russia_df = pd.DataFrame({
        "Name": names,
        "Gender": genders,
        "Reason": reasons,
        "Dates": dates,
        "Doc_title": doc_title,
        "Doc_number": doc_number,
        "Doc_url": doc_url,
        "Case_study": case_study,
        "Nationality": nationality
        
    })

    russia_df["Name"] = russia_df["Name"].str.replace(r"\(\)", "", regex=True).str.strip()
    russia_df["Gender"] = russia_df["Gender"].str.lower().str.strip()
    russia_df.replace({"██████": "unknown",}, inplace=True)
    russia_df = russia_df[~russia_df.apply(lambda row: (row == 'unknown').all(), axis=1)]
    russia_df["Dates"] = russia_df["Dates"].str.strip()
    russia_df["Dates"] = russia_df["Dates"].apply(format_date) 

    female_count = russia_df["Gender"].str.lower().value_counts().get

    # print(len(names), len(genders), len(reasons), len(dates))
    # print(russia_df.info())
    return russia_df.to_csv(csv_path, index=False)

    
extract_EU_russia_data()

