# 🎮 Caro Game - Multiplayer Network Game

Một game Caro (Gomoku) multiplayer được viết bằng Python với giao diện đồ họa sử dụng Pygame và kết nối mạng qua Socket.

## ✨ Tính năng

- 🎯 **Game Caro cổ điển**: 15x15 bàn cờ, 5 quân liên tiếp để thắng
- 🌐 **Multiplayer qua mạng**: 2 người chơi có thể chơi từ xa
- ⏰ **Hệ thống đếm giờ**: 40 giây cho mỗi lượt đi
- 🎨 **Giao diện đẹp**: Sử dụng Pygame với UI thân thiện
- 🔄 **Chơi lại**: Hỏi người chơi có muốn chơi ván mới không
- 🛡️ **Error handling**: Xử lý lỗi mạng và timeout tốt
- 📱 **Responsive**: Tương thích với nhiều độ phân giải

## 🚀 Cài đặt và chạy

### Yêu cầu hệ thống
```bash
Python 3.7+
pygame
```

### Cài đặt dependencies
```bash
pip install pygame
```

### Chạy game

1. **Khởi động Server** (máy host):
```bash
cd src
python server.py
```

2. **Khởi động Client** (mỗi người chơi):
```bash
cd src
python client.py
```

## 🎯 Cách chơi

### Luật chơi
- Mỗi người chơi lần lượt đặt quân cờ (X hoặc O) trên bàn cờ 15x15
- Người đầu tiên có 5 quân liên tiếp (ngang, dọc hoặc chéo) sẽ thắng
- Mỗi lượt có 40 giây để đi, hết giờ sẽ thua
- Có thể chơi nhiều ván liên tiếp

### Điều khiển
- **Chuột**: Click vào ô trống để đặt quân cờ
- **Y**: Đồng ý chơi lại
- **N**: Từ chối chơi lại
- **ESC/Close**: Thoát game

## 📁 Cấu trúc code

```
src/
├── server.py      # Server quản lý game
├── client.py      # Client với giao diện Pygame
└── common.py      # Utilities chung
```

## 🔧 Cấu hình

### Thay đổi cài đặt server
```python
# Trong server.py
server = GameServer(host="0.0.0.0", port=9999, timeout=30)
```

### Thay đổi cài đặt client
```python
# Trong client.py
client = CaroClient(host="127.0.0.1", port=9999, timeout=30)
```

**Chúc bạn chơi game vui vẻ! 🎉**