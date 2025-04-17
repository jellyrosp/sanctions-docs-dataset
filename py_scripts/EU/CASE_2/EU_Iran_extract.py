from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

html_path = "sanctions/EU/Iran/Iran_jointed_TEXT.html"

csv_path = "sanctions/EU/Iran/EU_iran_data1.csv"

def format_date(date_str):
    try:
        return datetime.strptime(date_str, "%d.%m.%Y").strftime("%d-%m-%Y")
    except ValueError:
        return "unknown"

def extract_EU_iran_data():

    with open(html_path, "r", encoding="utf-8") as file:
        html_content = file.read()
        soup = BeautifulSoup(html_content, "html.parser")
         
    names = []
    genders = []
    reasons = []
    dates = []
    doc_title = []
    doc_number = []
    doc_url = []
    case_study = []
    nationality = [] 

    table1 = soup.find("table", {"class": "borderOj"})
    rows_t1 = table1.find_all("tr")[1:]   

    table2 = soup.find("table", {"class": "borderOj2"})
    rows_t2 = table2.find_all("tr")[1:]   

    # NAMES FOR BOTH TABLES
    tables = soup.find_all("table") 
    for table in tables:
        rows = table.find_all("tr")[1:]

        for row in rows:
            cols = row.find_all("td")
            if len(cols) > 1:
                name_tag = cols[1].find("p", class_="tbl-norm")  # Get <p> inside the Name column
                if name_tag:
                    # Remove images inside the <p> tag
                    for img in name_tag.find_all("img"):
                        img.extract()
                    # Extract cleaned name
                    names.append(name_tag.get_text(strip=True))  
        
    # GENDER TABLE 1    
    for row in rows_t1:
        cols = row.find_all("td")
        if len(cols) > 1:  
            info_col = cols[2] 
            gender_found = False
            nat_found = False

            for p_tag in info_col.find_all("p", class_="tbl-norm"):
                text = p_tag.get_text(strip=True).replace(";", "")  

                # Check for gender
                if "gender" in text.lower():
                    parts = text.split(";")  
                    for part in parts:
                        if "gender" in part.lower():
                            gender_value = part.split(":", 1)[-1].strip()
                            genders.append(gender_value)
                            gender_found = True
                            break 

                # Check for nationality
                if "nationality" in text.lower():  # ✅ Fixed typo: "nationalitiy" → "nationality"
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


    # GENDER TABLE 2
    for row in rows_t2:
        cols = row.find_all("td")
        if len(cols) > 1:  
            info_col = cols[3] 
            gender_found = False
            nat_found = False

            for p_tag in info_col.find_all("p", class_="tbl-norm"):
                text = p_tag.get_text(strip=True).replace(";", "")  

                # Check for gender
                if "gender" in text.lower():
                    parts = text.split(";")  
                    for part in parts:
                        if "gender" in part.lower():
                            gender_value = part.split(":", 1)[-1].strip()
                            genders.append(gender_value)
                            gender_found = True
                            break 

                # Check for nationality
                if "nationality" in text.lower():  # ✅ Fixed typo: "nationalitiy" → "nationality"
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
           
    # REASON TABLE 1
    for row in rows_t1:
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
    # REASON TABLE 2
    for row in rows_t2:
        cols = row.find_all("td")
        if len(cols) > 1:  
            reason_tags = cols[4].find_all("p", class_="tbl-norm")  # Get all <p> elements inside column 4
            if reason_tags:
                reason_texts = []
                for reason_tag in reason_tags:
                    for img in reason_tag.find_all("img"):
                        img.extract()
                    reason_texts.append(reason_tag.get_text(strip=True))
                reasons.append("; ".join(reason_texts))  # Joining multiple reasons with "; "  

    # DATE TABLE 1
    for row in rows_t1:
            cols = row.find_all("td")
            if len(cols)  != 5:
                continue
            data_tag = cols[4].find("p", class_="tbl-left")
            text = data_tag.get_text(strip=True)     
            dates.append(text)  

            doc_title.append("COUNCIL_REGULATION_EU_36_2012_18_January_2012")
            doc_number.append("02012R0036-20241125")
            doc_url.append("http://data.europa.eu/eli/reg/2012/36/2024-11-25")
            case_study.append("Iran")  

    # DATE TABLE 2
    for row in rows_t2:
            cols = row.find_all("td")
            if len(cols) != 6:
                continue
            data_tag = cols[5].find("p", class_="tbl-left")
            text = data_tag.get_text(strip=True)     
            dates.append(text)    

            doc_title.append("COUNCIL_REGULATION_EU_359_2011_12 April_2011")
            doc_number.append("02011R0359-20240913")
            doc_url.append("http://data.europa.eu/eli/reg/2023/1529/2024-10-14")
            case_study.append("Iran")           

    iran_df = pd.DataFrame({
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

    iran_df["Name"] = iran_df["Name"].str.replace(r"\(\)", "", regex=True).str.strip()
    iran_df["Gender"] = iran_df["Gender"].str.lower().str.strip()
    iran_df["Dates"] = iran_df["Dates"].str.strip()
    iran_df["Dates"] = iran_df["Dates"].apply(format_date) 
    
    # print(len(names), len(genders), len(reasons), len(dates))
    # print(iran_df.info())
    # print(nationality)
    # print(f"Unknown: {nationality.count('unknown')}/{len(nationality)} ({(nationality.count('unknown') / len(nationality)) * 100:.2f}%)")

    return iran_df.to_csv(csv_path, index=False)


extract_EU_iran_data()

