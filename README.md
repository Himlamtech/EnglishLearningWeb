# FlashAI: Ứng dụng Flashcard hỗ trợ bởi AI

FlashAI là một ứng dụng kết hợp công nghệ AI để hỗ trợ học ngôn ngữ với chức năng flashcard. Phù hợp cho người học ngôn ngữ, sinh viên, và bất kỳ ai muốn nâng cao trải nghiệm học tập và viết lách.

## Tính năng

- **Tạo Flashcard**: Tạo flashcard từ các từ tiếng Anh hoặc tiếng Việt với bản dịch, hướng dẫn phát âm và từ đồng nghĩa
- **Học Flashcard**: Học, ôn tập và theo dõi tiến độ với các flashcard đã tạo
- **Chatbot Học Ngôn ngữ**: Luyện tập và nhận trợ giúp với các câu hỏi về ngôn ngữ
- **Kiểm tra Ngữ pháp**: Xác định và sửa lỗi ngữ pháp trong bài viết của bạn
- **Phát hiện AI**: Kiểm tra xác suất một văn bản được viết bởi AI
- **Nhân hóa Văn bản AI**: Làm cho nội dung do AI tạo ra nghe tự nhiên hơn
- **Nâng cao Bài viết**: Viết lại, diễn đạt lại hoặc nâng cao bất kỳ văn bản nào

## Công nghệ sử dụng

### Frontend
- Next.js (React)
- TypeScript
- Tailwind CSS
- React Hot Toast (thông báo)
- Headless UI (thành phần UI)
- Chart.js (hiển thị tiến độ)
- Framer Motion (hiệu ứng)

### Backend
- Python
- FastAPI
- OpenAI API (sử dụng YesScale API)
- Pandas (xử lý dữ liệu)
- Pydantic (xác thực dữ liệu)

## Bắt đầu

### Yêu cầu
- Node.js (v14+)
- Python (v3.8+)
- API key cho YesScale (để truy cập OpenAI API)

### Cài đặt

1. Clone repository:
```
git clone https://github.com/yourusername/flashai.git
cd flashai
```

2. Thiết lập backend:
```
cd backend
pip install -r requirements.txt
```

3. Tạo file `.env` trong thư mục backend với API key của bạn:
```
OPENAI_API_KEY=your_api_key_here
API_BASE_URL=https://api.yescale.io
```

4. Cài đặt các phụ thuộc frontend:
```
cd frontend
npm install
```

5. Khởi động ứng dụng (từ thư mục gốc):
```
# Trên Linux/MacOS
./app.sh

# Trên Windows
app.bat
```

6. Mở trình duyệt và truy cập `http://localhost:3000`

## Cách sử dụng

### Tạo Flashcard
1. Đi đến "Flashcard Generation" trong thanh điều hướng
2. Nhập một từ bằng tiếng Anh hoặc tiếng Việt
3. Chọn ngôn ngữ đích hoặc sử dụng tự động phát hiện
4. Nhấp "Generate Flashcard"

### Học Flashcard
1. Đi đến "Learn Flashcard" trong thanh điều hướng
2. Lật qua các flashcard để xem bản dịch và từ đồng nghĩa
3. Đánh dấu thẻ là đã học khi bạn đã thành thạo

### Sử dụng các tính năng khác
- Mỗi tính năng có thể truy cập thông qua thanh điều hướng
- Làm theo hướng dẫn trên màn hình cho từng công cụ

## Cấu trúc dự án

```
FlashAI
├── frontend/              # Frontend (Next.js)
│   ├── app/               # Mã ứng dụng
│   │   ├── api/           # Các hàm client API
│   │   ├── components/    # Các component React có thể tái sử dụng
│   │   ├── pages/         # Các trang/route
│   │   ├── styles/        # Style toàn cục
│   │   └── utils/         # Các hàm tiện ích
│   ├── pages/             # Các trang Next.js
│   ├── public/            # Tài nguyên tĩnh
│   ├── package.json       # Phụ thuộc frontend
│   ├── tailwind.config.js # Cấu hình Tailwind CSS
│   └── tsconfig.json      # Cấu hình TypeScript
├── backend/               # Backend Python
│   ├── config.py          # Cấu hình
│   ├── main.py            # Ứng dụng FastAPI
│   ├── models.py          # Các model Pydantic
│   ├── openai_client.py   # Tích hợp OpenAI
│   ├── requirements.txt   # Phụ thuộc Python
│   ├── run.py             # Script khởi động server
│   ├── storage.py         # Lưu trữ dữ liệu
│   └── test_api.py        # Kiểm thử API
├── app.sh                 # Script khởi động cho Linux/MacOS
├── app.bat                # Script khởi động cho Windows
└── README.md              # Tài liệu dự án
```

## Giấy phép

Dự án này được cấp phép theo Giấy phép MIT

---

Được xây dựng với ❤️ sử dụng Next.js, FastAPI và OpenAI
