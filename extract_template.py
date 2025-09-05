import bs4
import pandas as pd
import re
import os
import csv

def extract_data_from_html(html_path, output_path=None):
    """
    Trích xuất dữ liệu từ file HTML có cấu trúc bảng phân cấp và lưu vào CSV
    
    Args:
        html_path (str): Đường dẫn đến file HTML
        output_path (str, optional): Đường dẫn file CSV đầu ra. Nếu None, sẽ lấy tên từ file HTML
    
    Returns:
        pandas.DataFrame: DataFrame chứa dữ liệu đã trích xuất
    """
    # Nếu không có output_path, tạo tên từ html_path
    if output_path is None:
        base_name = os.path.splitext(os.path.basename(html_path))[0]
        output_path = f"{base_name}.csv"
    
    # Đọc file HTML
    with open(html_path, encoding="utf-8") as f:
        soup = bs4.BeautifulSoup(f, "html.parser")
    
    # Tìm bảng dữ liệu - điều chỉnh selector này tùy theo HTML của bạn
    table = soup.find("table")
    if not table:
        raise ValueError("Không tìm thấy bảng dữ liệu trong HTML")
    
    # Lấy tất cả các hàng
    rows = table.find_all("tr")
    if not rows:
        raise ValueError("Không tìm thấy dòng dữ liệu trong bảng")
    
    # Xác định số cột tối đa để làm tiền xử lý
    max_columns = 0
    for row in rows:
        cells = row.find_all(["td", "th"])
        max_columns = max(max_columns, len(cells))
    
    # Nếu không tìm thấy cột nào, thoát
    if max_columns == 0:
        raise ValueError("Không tìm thấy cột dữ liệu trong bảng")
    
    # Phân tích dữ liệu từ bảng
    results = []
    group_stack = [""] * (max_columns - 1)  # Stack để lưu trữ các nhóm cấp độ
    
    for row in rows:
        cells = row.find_all(["td", "th"])
        if not cells:
            continue
        
        # Lấy nội dung các ô trong hàng
        cell_values = [cell.get_text(strip=True) for cell in cells]
        
        # Tìm cột giá trị (VALUE) - thường là cột cuối cùng có dữ liệu số
        value = None
        value_col = None
        
        for i in range(len(cell_values) - 1, 0, -1):
            if cell_values[i]:
                # Kiểm tra xem có phải là số không (bao gồm số âm và số thập phân)
                # hoặc giá trị NULL/N/A
                value_text = cell_values[i]
                if (re.match(r'^-?\d+\.?\d*$', value_text) or 
                    value_text.upper() in ["NULL", "N/A", "-"]):
                    value = value_text
                    value_col = i
                    break
        
        # Nếu không tìm thấy giá trị, bỏ qua hàng này
        if value_col is None:
            continue
        
        # Lấy tất cả các ô có dữ liệu trong hàng, trước cột giá trị
        group_cols = []
        for i in range(0, value_col):
            if cell_values[i]:
                group_cols.append(cell_values[i])
        
        # Cập nhật group_stack
        for i, group in enumerate(group_cols):
            if i < len(group_stack):
                group_stack[i] = group
                
                # Xóa các nhóm con sau khi cập nhật nhóm cha
                for j in range(i + 1, len(group_stack)):
                    group_stack[j] = ""
        
        # Nếu không có nhóm nào, bỏ qua hàng này
        if not any(group_stack):
            continue
        
        # Tạo dòng dữ liệu
        row_data = {}
        for i in range(len(group_stack)):
            row_data[f"DATA_GROUP_L{i+1}"] = group_stack[i]
        row_data["VALUE"] = value
        
        results.append(row_data)
    
    # Tạo DataFrame
    df = pd.DataFrame(results)
    
    # Lưu vào CSV
    df.to_csv(output_path, index=False)
    
    return df

def extract_with_mapping(html_path, output_path=None, template_path=None, 
                         value_mapping=None, name_mapping=None):
    """
    Trích xuất dữ liệu từ HTML với ánh xạ giá trị từ template
    
    Args:
        html_path (str): Đường dẫn file HTML
        output_path (str, optional): Đường dẫn file CSV đầu ra
        template_path (str, optional): Đường dẫn file CSV template
        value_mapping (dict, optional): Ánh xạ từ giá trị HTML sang giá trị đầu ra
        name_mapping (dict, optional): Ánh xạ tên nhóm
    
    Returns:
        pandas.DataFrame: DataFrame chứa dữ liệu đã trích xuất
    """
    # Đọc file template nếu có
    template_data = []
    if template_path and os.path.exists(template_path):
        try:
            template_df = pd.read_csv(template_path)
            template_data = template_df.to_dict('records')
        except Exception as e:
            print(f"Không thể đọc file template: {e}")
    
    # Đọc file HTML
    with open(html_path, encoding="utf-8") as f:
        soup = bs4.BeautifulSoup(f, "html.parser")
    
    # Tìm bảng dữ liệu
    table = soup.find("table")
    if not table:
        raise ValueError("Không tìm thấy bảng dữ liệu trong HTML")
    
    # Lấy tất cả các hàng
    rows = table.find_all("tr")
    
    # Nếu có template_data, chỉ cần áp dụng ánh xạ giá trị
    if template_data:
        results = []
        
        # Tạo mapping giữa HTML và giá trị đầu ra
        html_values = []
        for row in rows:
            cells = row.find_all(["td", "th"])
            if not cells:
                continue
                
            cell_values = [cell.get_text(strip=True) for cell in cells]
            
            # Tìm cột giá trị
            for i in range(len(cell_values) - 1, 0, -1):
                if cell_values[i] and re.match(r'^-?\d+\.?\d*$', cell_values[i]):
                    html_values.append(cell_values[i])
                    break
        
        # Nếu có value_mapping, sử dụng nó
        if value_mapping:
            for item in template_data:
                # Giữ nguyên cấu trúc nhóm
                new_item = item.copy()
                
                # Nếu giá trị nằm trong mapping
                html_value = None
                for hv in html_values:
                    if hv in value_mapping and value_mapping[hv] == item["VALUE"]:
                        html_value = hv
                        break
                
                # Cập nhật giá trị nếu tìm thấy
                if html_value:
                    new_item["VALUE"] = item["VALUE"]
                
                results.append(new_item)
        else:
            # Nếu không có value_mapping, thì đơn giản là sử dụng lại template
            results = template_data
    else:
        # Nếu không có template, tạo dữ liệu mới
        results = extract_data_from_html(html_path, None).to_dict('records')
    
    # Tạo DataFrame
    df = pd.DataFrame(results)
    
    # Lưu vào CSV
    if output_path:
        df.to_csv(output_path, index=False)
    
    return df

if __name__ == "__main__":
    # Ví dụ sử dụng
    # 1. Sử dụng phương pháp tổng quát
    # df = extract_data_from_html("example.html", "output.csv")
    
    # 2. Sử dụng phương pháp ánh xạ từ template
    # df = extract_with_mapping("example.html", "output.csv", "template.csv")
    
    print("Chọn phương pháp trích xuất:")
    print("1. Tự động phân tích cấu trúc HTML")
    print("2. Sử dụng template từ file CSV")
    
    choice = input("Lựa chọn của bạn (1/2): ")
    
    html_file = input("Đường dẫn file HTML: ")
    output_file = input("Đường dẫn file CSV đầu ra: ")
    
    if choice == "1":
        df = extract_data_from_html(html_file, output_file)
        print(f"Đã lưu kết quả vào {output_file}")
        print(df.head())
    elif choice == "2":
        template_file = input("Đường dẫn file template CSV: ")
        df = extract_with_mapping(html_file, output_file, template_file)
        print(f"Đã lưu kết quả vào {output_file}")
        print(df.head())
    else:
        print("Lựa chọn không hợp lệ")
