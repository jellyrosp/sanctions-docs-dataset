from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

def format_date(date_str):
    try:
        return datetime.strptime(date_str, "%d.%m.%Y").strftime("%d-%m-%Y")
    except ValueError:
        return "unknown"

def html2csv_extract(html_path, csv_path, d_title, d_number, d_url, case_st):
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
        rows = table.find_all("tr")[1:]  # Skip header row

        # NAMES
        # for row in rows:
        #     cols = row.find_all("td")
        #     if len(cols) > 1:
        #         name_tag = cols[1].find("p", class_="tbl-norm")
                
        #         if name_tag:
        #             name = name_tag.get_text(strip=True)
        #         else:
        #             name = "unknown"
                
        #         names.append(name)
        #         doc_title.append(d_title)
        #         doc_number.append(d_number)
        #         doc_url.append(d_url)
        #         case_study.append(case_st)

        # NAMES 2 (UKRAINE)
        for row in rows:
            cols = row.find_all("td")
            if len(cols) > 1:
                name_cell = cols[1]
                name = "unknown"

                # Find all <p class="tbl-norm"> in the second column
                name_paragraphs = name_cell.find_all("p", class_="tbl-norm")
                for p in name_paragraphs:
                    # Remove any images in the paragraph
                    for img in p.find_all("img"):
                        img.extract()

                    # Get the cleaned text
                    text = p.get_text(strip=True)
                    if text:
                        name = text  # Use the first non-empty one
                        break  # Stop after finding the first valid name

                names.append(name)
                doc_title.append(d_title)
                doc_number.append(d_number)
                doc_url.append(d_url)
                case_study.append(case_st)
            

        # GENDER
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

        # REASON
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
                if not reason_tags:
                    reasons.append("unknown")         

        # DATE
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

    # print("LENGTH CHECK:")
    # print("names:", len(names))
    # print("genders:", len(genders))
    # print("reasons:", len(reasons))
    # print("dates:", len(dates))
    # print("doc_title:", len(doc_title))
    # print("doc_number:", len(doc_number))
    # print("doc_url:", len(doc_url))
    # print("case_study:", len(case_study))
    # print("nationality:", len(nationality))


    num_rows = len(names)
    df = pd.DataFrame({
        "Name": names,
        "Gender": genders,
        "Reason": reasons,
        "Activity_based": [""] * num_rows,
        "Profit_based": [""] * num_rows,
        "Family_member_sanctions": [""] * num_rows,
        "Dates": dates,
        "Doc_title": doc_title,
        "Doc_number": doc_number,
        "Doc_url": doc_url,
        "Case_Study": case_study,
        "Nationality": nationality
        
    })

    df["Name"] = df["Name"].str.replace(r"\(\)", "", regex=True).str.strip()
    df["Gender"] = df["Gender"].str.lower().str.strip()
    df.replace({"██████": "unknown",}, inplace=True)
    df = df[~df.apply(lambda row: (row == 'unknown').all(), axis=1)]
    df["Dates"] = df["Dates"].str.strip()
    df["Dates"] = df["Dates"].apply(format_date)   

    #print(df.info())
    return df.to_csv(csv_path,index=False)                                       



html_path = "sanctions/EU/Ukraine/Consolidated_TEXT_32014R0269_EN_24_02_2025_CLEANED.html"
csv_path = "sanctions/EU/Ukraine/EU_Ukraine_data.csv"
doc_title = "COUNCIL_REGULATION_EU_269_2014_of_17_March_2014"
doc_num = "02014R0269-20250316"
url = "http://data.europa.eu/eli/reg/2014/269/2025-03-16"
case_study = "Ukraine"


html2csv_extract(html_path, csv_path, doc_title, doc_num, url, case_study)
