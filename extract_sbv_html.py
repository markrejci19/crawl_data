import bs4
import pandas as pd

def extract_sbv_html(html_path):
    with open(html_path, encoding="utf-8") as f:
        soup = bs4.BeautifulSoup(f, "html.parser")

    table = soup.find("table", class_="jrPage")
    rows = table.find_all("tr")

    results = []
    current_main_group = ""  # To track the current main section
    group_stack = [""] * 6  # Stack to maintain hierarchy

    for tr in rows:
        tds = tr.find_all("td")
        if len(tds) < 5:
            continue

        # Look for text content and value in this row
        text_content = ""
        value_content = ""
        padding_level = 0
        is_main_section = False
        
        for i, td in enumerate(tds):
            text = td.get_text(strip=True)
            if not text:
                continue
                
            style = td.get('style', '')
            
            # Check if this is a main section header (has background color)
            if 'background-color: #E7E8E9' in style:
                # Remove letter prefixes like "A. ", "B. ", "C. ", etc.
                clean_text = text
                if len(text) > 3 and text[1:3] == ". ":
                    clean_text = text[3:]
                
                current_main_group = clean_text
                is_main_section = True
                text_content = clean_text
                
                # Reset group stack when entering new main section
                group_stack = [clean_text] + [""] * 5
                
                # Look for value in the next cells
                for j in range(i+1, len(tds)):
                    val_text = tds[j].get_text(strip=True)
                    if val_text and (val_text.replace('.', '', 1).replace('-', '', 1).replace(',', '').isdigit() or val_text.upper() == "NULL"):
                        value_content = val_text if val_text.upper() != "NULL" else "NULL"
                        break
                break
            
            # Check for regular items with padding
            elif 'padding-left:' in style:
                # Extract padding value
                import re
                padding_match = re.search(r'padding-left:\s*(\d+)px', style)
                if padding_match:
                    padding_pixels = int(padding_match.group(1))
                    
                    # Map padding to hierarchy level
                    if padding_pixels == 20:
                        padding_level = 1  # DATA_GROUP_L2
                    elif padding_pixels == 57:
                        padding_level = 1  # Also DATA_GROUP_L2 (sub-items like "ròng")
                    elif padding_pixels == 90:
                        padding_level = 2  # DATA_GROUP_L3
                    elif padding_pixels == 125:
                        padding_level = 3  # DATA_GROUP_L4
                    elif padding_pixels == 160:
                        padding_level = 4  # DATA_GROUP_L5
                    
                    text_content = text
                    
                    # Look for value in the next cells
                    for j in range(i+1, len(tds)):
                        val_text = tds[j].get_text(strip=True)
                        if val_text and (val_text.replace('.', '', 1).replace('-', '', 1).replace(',', '').isdigit() or val_text.upper() == "NULL"):
                            value_content = val_text if val_text.upper() != "NULL" else "NULL"
                            break
                    break

        # Add the data row if we found both text and value
        if text_content and value_content:
            if is_main_section:
                # This is a main section summary row
                results.append({
                    "DATA_GROUP_L1": group_stack[0],
                    "DATA_GROUP_L2": group_stack[1],
                    "DATA_GROUP_L3": group_stack[2],
                    "DATA_GROUP_L4": group_stack[3],
                    "DATA_GROUP_L5": group_stack[4],
                    "DATA_GROUP_L6": group_stack[5],
                    "VALUE": value_content
                })
            else:
                # Update the group stack at the appropriate level
                if padding_level > 0:
                    # Clear deeper levels
                    for i in range(padding_level, 6):
                        group_stack[i] = ""
                    # Set this level
                    group_stack[padding_level] = text_content
                
                results.append({
                    "DATA_GROUP_L1": group_stack[0],
                    "DATA_GROUP_L2": group_stack[1],
                    "DATA_GROUP_L3": group_stack[2],
                    "DATA_GROUP_L4": group_stack[3],
                    "DATA_GROUP_L5": group_stack[4],
                    "DATA_GROUP_L6": group_stack[5],
                    "VALUE": value_content
                })

    df = pd.DataFrame(results)
    return df

if __name__ == "__main__":
    df = extract_sbv_html("sbv_data_IV_2024_v1_20250904.html")
    df.to_csv("sbv_data_IV_2024_v1_20250904.csv", index=False)
    print(df.head(20))