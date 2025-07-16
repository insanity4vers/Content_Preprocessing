import time
import pandas as pd
import argparse
import os
from dotenv import load_dotenv
from google import generativeai


# Load environment variables from .env file
load_dotenv()

# --- Content generation ---
def process_content(input_path, output_path):
    try:
        df = pd.read_excel(input_path, usecols=['content'])
    except ValueError:
        raise ValueError("Columns 'content' not found in excel file")

    if df.empty:
        print("No content to process.")
        return
    df.dropna(subset=['content'], inplace=True)
    df.drop_duplicates(subset='content', ignore_index=True, inplace=True)

    api_key = os.getenv('API_KEY')
    if not api_key:
        raise ValueError("API_KEY not found in environment variables. Please check your .env file.")

    generativeai.configure(api_key=api_key)
    model = generativeai.GenerativeModel(model_name='gemini-2.5-pro')

    requests = df['content'].tolist()
    generated_content_list = []

    # Process each content request
    for i, request_text in enumerate(requests):
        print(f"Đang xử lý yêu cầu {i + 1}/{len(requests)}: '{str(request_text)[:60]}...'")

        try:
            response = model.generate_content(f"Tạo một bài đăng bằng tiếng Việt độ dài tối đa 500 ký tự bao gồm hashtag, giới thiệu ngắn gọn về sản phẩm theo nội dung và liên kết mua hàng sau đây: \n{request_text}\n Lưu ý: chỉ trả về một kết quả duy nhất không nói gì khác ngoài nội dung bài đăng, không cần thêm bất kỳ thông tin nào khác.")

            if response.parts:
                content = response.text
                print("✅ Đã tạo nội dung thành công.")
            else:
                block_reason = "Không rõ"
                if response.prompt_feedback and response.prompt_feedback.block_reason:
                    block_reason = response.prompt_feedback.block_reason.name
                content = f"ERROR: BLOCKED_BY_SAFETY_FILTER ({block_reason})"
                print(f"❌ Bị chặn vì lý do an toàn: {block_reason}")

            generated_content_list.append({
                'id': i + 1,
                'request': request_text,
                'content': content
            })

        except Exception as e:
            print(f"❌ Lỗi API nghiêm trọng: {e}")
            generated_content_list.append({
                'id': i + 1,
                'request': request_text,
                'content': f"ERROR: API_CALL_FAILED ({e})"
            })
        print(f"✅ Đã hoàn thành yêu cầu {i + 1}/{len(requests)}.")
        if i < len(requests) - 1:
            print("Đang tạm dừng 30 giây để tránh quá tải API...")
            time.sleep(30)

    print("\nHoàn tất việc tạo nội dung.")

    try:
        print(f"Đang ghi kết quả vào file Excel: {output_path}...")
        results_df = pd.DataFrame(generated_content_list)
        results_df.to_excel(output_path, index=False, engine='openpyxl')
        print(f"✅ Đã ghi toàn bộ kết quả thành công vào file: {output_path}")
    except Exception as e:
        print(f"Lỗi: Không thể ghi vào file Excel {output_path}: {e}")

# --- Groups URL processing ---
def process_group_url(input_path, output_path):
    try:
        df = pd.read_excel(input_path, usecols=['url'])
    except ValueError:
        raise ValueError("Column 'url' not found in excel file")
    if df.empty:
        print("No URLs to process.")
        return
    df.dropna(subset=['url'], inplace=True)
    df.drop_duplicates(subset='url', ignore_index=True, inplace=True)
    df['url'] = df['url'].str.split('?', n=1).str[0]
    df.to_excel(output_path, index=False)
    print(f"Finished processing and saving the results to {output_path}")

# --- Main CLI ---
def main():
    parser = argparse.ArgumentParser(description='Contents processing.')
    parser.add_argument('--ci', type=str, default='contents_input.xlsx', help='Post contents input file path')
    parser.add_argument('--co', type=str, default='contents.xlsx', help='Post contents output file path')
    parser.add_argument('--gi', type=str, default='group_urls_input.xlsx', help='Group url input file path')
    parser.add_argument('--go', type=str, default='group_urls.xlsx', help='Group url output file path')
    args = parser.parse_args()
    try:
        process_group_url(args.gi, args.go)
        process_content(args.ci, args.co)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
