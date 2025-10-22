import pandas as pd

# Đọc dữ liệu, bỏ qua dòng đầu, header ở dòng 1
df = pd.read_csv('402.csv')

# Lấy dữ liệu từ cột 0 đến cột 10
df = df.iloc[:, 0:11]

# Lấy giá trị distinct của cột name_table (cột 11)
data_group = pd.read_csv('402.csv')[df.columns[0]].unique()[0]
df['DATA_GROUP'] = data_group

# Đánh dấu group
L1_list = ["DƯ NỢ", "RÚT VỐN TRONG KỲ", "TỔNG TRẢ NỢ TRONG KỲ"]
L2_list = ["Tổng trả nợ gốc trong kỳ", "Tổng trả lãi và phí trong kỳ"]
L3_list = ["Nợ nước ngoài", "Nợ trong nước"]

df['GROUP'] = None
df['L1'] = None
df['L2'] = None
df['L3'] = None

last_L1 = None
last_L2 = None
for idx, row in df.iterrows():
	val = str(row[df.columns[0]]).strip()
	if val in L1_list:
		df.at[idx, 'GROUP'] = 'L1'
		last_L1 = val
		last_L2 = None
		df.at[idx, 'L1'] = last_L1
	elif val in L2_list:
		df.at[idx, 'GROUP'] = 'L2'
		df.at[idx, 'L1'] = last_L1
		last_L2 = val
		df.at[idx, 'L2'] = last_L2
	elif val in L3_list:
		df.at[idx, 'GROUP'] = 'L3'
		df.at[idx, 'L3'] = val
		if last_L2:
			df.at[idx, 'L2'] = last_L2
			df.at[idx, 'L1'] = last_L1
		else:
			df.at[idx, 'L1'] = last_L1
df = df.drop(df.columns[0], axis=1)
df = df.drop('GROUP', axis=1)
df.to_csv('output.csv', index=False)