import bs4
import pandas as pd

def extract_sbv_html(html_path):
    with open(html_path, encoding="utf-8") as f:
        soup = bs4.BeautifulSoup(f, "html.parser")

    table = soup.find("table", class_="jrPage")
    rows = table.find_all("tr")

    results = []
    group_stack = [""] * 6  # DATA_GROUP_L1 -> DATA_GROUP_L6

    for tr in rows:
        tds = tr.find_all("td")
        if len(tds) < 5:
            continue

        # Lấy text các cột
        cols = [td.get_text(strip=True) for td in tds]
        # Xác định vị trí cột chỉ tiêu và giá trị
        # Chỉ tiêu thường ở cột 3 hoặc 4, giá trị ở cột 5
        value = None
        for i in range(len(cols)-1, 1, -1):
            # Tìm giá trị số hoặc số âm hoặc NULL
            if cols[i].replace('.', '', 1).replace('-', '', 1).isdigit() or cols[i].upper() == "NULL":
                value = cols[i] if cols[i].upper() != "NULL" else "NULL"
                value_col = i
                break
        else:
            continue

        # Xác định các group
        # Tìm chỉ tiêu (từ trái sang phải, bỏ qua cột rỗng)
        group_cols = []
        for i in range(2, value_col):
            if cols[i]:
                group_cols.append(cols[i])
        # Đẩy group vào stack
        for i, g in enumerate(group_cols):
            group_stack[i] = g
        # Xóa các group sâu hơn nếu không có dữ liệu
        for i in range(len(group_cols), 6):
            group_stack[i] = ""

        # Nếu là dòng tổng (ví dụ: "A. Cán cân vãng lai"), chỉ điền group 1
        if group_cols and not any(group_stack[1:]):
            group_stack[0] = group_cols[0]
            group_stack[1:] = [""] * 5

        results.append({
            "DATA_GROUP_L1": group_stack[0],
            "DATA_GROUP_L2": group_stack[1],
            "DATA_GROUP_L3": group_stack[2],
            "DATA_GROUP_L4": group_stack[3],
            "DATA_GROUP_L5": group_stack[4],
            "DATA_GROUP_L6": group_stack[5],
            "VALUE": value
        })

    df = pd.DataFrame(results)
    return df

if __name__ == "__main__":
    df = extract_sbv_html("sbv_data_IV_2024_v1_20250904.html")
    df.to_csv("sbv_data_IV_2024_v1_20250904.csv", index=False)
    print(df.head(20))