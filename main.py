import random
import pandas as pd
import argparse


# --- Content extraction and URL handling ---
def extract_content_and_url(series):
    urls = series.str.extract(r'(https?://\S+)', expand=False).fillna('')
    contents = series.str.replace(r'(https?://\S+)', '', regex=True).str.strip()
    return contents, urls

def add_or_replace(series, mask):
    mask_org = series.str.startswith('Xem ngay')
    series = series.where(~mask_org, mask + series.str[len('Xem ngay'):])
    mask_new = series.str.startswith(mask)
    series = series.where(mask_new, mask + series)
    return series

# --- URL utilities ---
def remove_query_string(url_series):
    return url_series.str.split('?', n=1).str[0]

# --- Excel processing ---
def process_content_excel(input_path, output_path, masks):
    df_content = pd.read_excel(input_path, usecols=['content'])
    df_content.dropna(inplace=True)
    df_content.drop_duplicates(inplace=True)
    contents, urls = extract_content_and_url(df_content['content'].astype(str))
    content_full = contents.where(urls == '', contents + '\n' + urls)
    content_full = add_or_replace(content_full, random.choice(masks))
    content_full.to_frame('content').to_excel(output_path, index=False)
    print(f"Đã xử lý xong nội dung và lưu kết quả vào {output_path}")

def process_url_excel(input_path, output_path):
    try:
        df = pd.read_excel(input_path, usecols=['url'])
    except ValueError:
        raise ValueError("Không tìm thấy cột 'url' trong file excel.")
    df['url'] = remove_query_string(df['url'])
    df.drop_duplicates(subset='url', ignore_index=True, inplace=True)
    df.to_excel(output_path, index=False)
    print(f"Đã xử lý xong và lưu kết quả vào {output_path}")

# --- Main CLI ---
def main():
    parser = argparse.ArgumentParser(description='Contents processing.')
    parser.add_argument('--ci', type=str, default='contents_input.xlsx', help='Post contents input Excel file path')
    parser.add_argument('--co', type=str, default='contents_output.xlsx', help='Post contents output Excel file path')
    parser.add_argument('--gi', type=str, default='group_urls_input.xlsx', help='Group url input Excel file path')
    parser.add_argument('--go', type=str, default='group_urls_output.xlsx', help='Group url output Excel file path')
    args = parser.parse_args()
    masks = [
        'SALE CỰC SHOCK MÚC NGAY THÔI!!!',
        'DEAL CỰC HỜI SALE CỰC SỐC!!!',
        'SIÊU SALE CỰC SỐC!!!',
        'ĐỪNG BỎ LỠ CƠ HỘI!!!',
    ]
    try:
        process_content_excel(args.ci, args.co, masks)
        process_url_excel(args.gi, args.go)
    except Exception as e:
        print(f"Lỗi: {e}")

if __name__ == '__main__':
    main()
