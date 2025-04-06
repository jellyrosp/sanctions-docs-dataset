from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

html_path = "sanctions/UN_EU/DPRK/Consolidated_TEXT_ 32017R1509_13.09.2024/Consolidated_TEXT_32017R1509_13.09.2024_CLEANED.html"

csv_path = "sanctions/UN_EU/UN_EU_DPRK_data.csv"

def format_date(date_str):
    try:
        return datetime.strptime(date_str, "%d.%m.%Y").strftime("%d-%m-%Y")
    except ValueError:
        return "unknown"
    
def extract_gender(info_col):
    gender = "unknown"
    for p_tag in info_col.find_all("p", class_="tbl-norm"):
        text = p_tag.get_text(strip=True).replace(";", "")
        if "██████" in text:
            gender = "unknown"
            break
        if "gender" in text.lower():
            parts = text.split(";")
            for part in parts:
                if "gender" in part.lower():
                    gender = part.split(":", 1)[-1].strip().lower()
                    break 
    return gender 

def extract_reason(cols, col_index):
    reason_texts = []
    for reason_tag in cols[col_index].find_all("p", class_="tbl-norm"):
        for img in reason_tag.find_all("img"):
            img.extract()
        reason_texts.append(reason_tag.get_text(strip=True))
    reason = "; ".join(reason_texts) if reason_texts else "unknown"   
    return reason   


def extract_date(cols, col_index):
    date_tag = cols[col_index].find("p", class_="tbl-left")
    if date_tag:
        for img in date_tag.find_all("img"):
            img.extract()
        date_text = date_tag.get_text(strip=True)
        if not date_text or date_text.strip() in {"██████", "None", "-", "--"}:
            date = "unknown"
        else:
            date = date_text.strip()
    else:
        date = "unknown"
    return date    



def extract_UN_EU_DPRK_data():

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


    for table in tables:
        rows = table.find_all("tr")[1:]

        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 2:
                continue  # Skip rows that are too short to extract a name

            # --- Name ---
            name_tag = cols[1].find("p", class_="tbl-norm")
            if name_tag:
                for img in name_tag.find_all("img"):
                    img.extract()
                name = name_tag.get_text(strip=True)
            else:
                name = "unknown"


             # --- Gender ---
            
            if len(cols) == 6:
                info_col = cols[3]
                gender = extract_gender(info_col)
            else:
                info_col = cols[2]
                gender = extract_gender(info_col)               


            # --- Reason ---
            reason_texts = []
            if len(cols) == 6:
                reason = extract_reason(cols, 5)
            else:
                reason = extract_reason(cols, 4)   
     

            # --- Date ---
            if len(cols) == 6:
                date = extract_date(cols, 4)
            else:
                date = extract_date(cols, 3)  




            

        # Append all together
            names.append(name)
            genders.append(gender)
            reasons.append(reason)
            dates.append(date)
            doc_title.append("COUNCIL_REGULATION_EU_2017_1509_30_August_2017")
            doc_number.append("02017R1509-20240913")
            doc_url.append("http://data.europa.eu/eli/reg/2017/1509/2024-09-13") 
            case_study.append("DPRK")

    # print(len(names))
    # print(len(genders))
    # print(len(reasons))
    # print(len(dates))
    #print(dates)
    #print(reasons)

   

    # DPRK_df = pd.DataFrame({
    #     "Name": names,
    #     "Gender": genders,
    #     "Reason": reasons,
    #     "Dates": dates,
    #     "Doc_title": doc_title,
    #     "Doc_number": doc_number,
    #     "Doc_url": doc_url,
    #     "Case_study": case_study
        
    #  })  
    
    num_rows = len(names)

    DPRK_df = pd.DataFrame({
        "Name": names,
        "Gender": genders,
        "Reason": reasons,
        "Direct": [""] * num_rows,
        "Indirect": [""] * num_rows,
        "Activity": [""] * num_rows,
        "Profit": [""] * num_rows,
        "Family_status": [""] * num_rows,
        "Dates": dates,
        "Doc_title": doc_title,
        "Doc_number": doc_number,
        "Doc_url": doc_url,
        "Case_study": case_study
    })  

    DPRK_df["Name"] = DPRK_df["Name"].str.replace(r"\(\)", "", regex=True).str.strip()
    DPRK_df["Gender"] = DPRK_df["Gender"].str.lower().str.strip()
    DPRK_df.replace({"██████": "unknown",}, inplace=True)
    DPRK_df = DPRK_df[~DPRK_df.apply(lambda row: (row == 'unknown').all(), axis=1)]
    DPRK_df["Dates"] = DPRK_df["Dates"].str.strip()
    DPRK_df["Dates"] = DPRK_df["Dates"].apply(format_date) 
    # #DPRK_df = DPRK_df[~DPRK_df.isin(["unknown"]).any(axis=1)]

    # print(len(names), len(genders), len(reasons), len(dates))
    #print(DPRK_df.info())
    return DPRK_df.to_csv(csv_path, index=False)


extract_UN_EU_DPRK_data()

