import pandas as pd
import argparse


def extract_content_and_url(series):
    urls = series.str.extract(r'(https?://\S+)', expand=False).fillna('')
    contents = series.str.replace(r'(https?://\S+)', '', regex=True).str.strip()
    return contents, urls

def add_or_replace_sale_soc(series):
    mask_xemngay = series.str.startswith('Xem ngay')
    series = series.mask(mask_xemngay, 'Sale SỐC' + series.str[len('Xem ngay'):])
    mask_salesoc = series.str.startswith('Sale SỐC')
    series = series.mask(~mask_salesoc, 'Sale SỐC' + series)
    return series

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Tách nội dung và URL từ file Excel.')
    parser.add_argument('--input', type=str, default='input.xlsx', help='Đường dẫn tới file Excel đầu vào (mặc định: input.xlsx)')
    parser.add_argument('--output', type=str, default='contents.xlsx', help='Đường dẫn tới file Excel đầu ra (mặc định: contents.xlsx)')
    args = parser.parse_args()

    try:
        df = pd.read_excel(args.input)
        contents, urls = extract_content_and_url(df['content'].astype(str))
        content_full = contents.where(urls == '', contents + '\n' + urls)
        content_full = add_or_replace_sale_soc(content_full)
        content_full = content_full.drop_duplicates()
        content_full.to_frame('content').to_excel(args.output, index=False)
        print(f"Đã xử lý xong và lưu kết quả {args.output}")
    except Exception as e:
        print(f"Lỗi: {e}")
