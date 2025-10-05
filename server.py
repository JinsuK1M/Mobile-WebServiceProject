import socket
import os
from datetime import datetime
from requests_toolbelt.multipart import decoder

# -----------------------------
# 설정
# -----------------------------
HOST = '127.0.0.1'
PORT = 8000

REQUEST_DIR = 'request'
IMAGE_DIR = 'received_images'

os.makedirs(REQUEST_DIR, exist_ok=True)
os.makedirs(IMAGE_DIR, exist_ok=True)

# -----------------------------
# 소켓 서버 생성
# -----------------------------
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print(f"Server running on {HOST}:{PORT}")

    while True:
        conn, addr = s.accept()
        with conn:
            print(f"Connected by {addr}")
            data = b''

            # 클라이언트 데이터 수신
            while True:
                packet = conn.recv(4096)
                if not packet:
                    break
                data += packet

            # -----------------------------
            # 실습 1: 요청 데이터 .bin 파일로 저장
            # -----------------------------
            timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
            bin_file_path = os.path.join(REQUEST_DIR, f"{timestamp}.bin")
            with open(bin_file_path, 'wb') as f:
                f.write(data)
            print(f"Saved request to {bin_file_path}")

            # -----------------------------
            # 실습 2: multipart 이미지 저장
            # -----------------------------
            # Content-Type 헤더 찾기
            headers_end = data.find(b'\r\n\r\n')
            if headers_end != -1:
                headers = data[:headers_end].decode(errors='ignore').split("\r\n")
                content_type = None
                for h in headers:
                    if h.lower().startswith('content-type: multipart/form-data'):
                        content_type = h.split(":", 1)[1].strip()
                        break

                if content_type:
                    try:
                        decoder = decoder.MultipartDecoder(data, content_type)
                        for part in decoder.parts:
                            disposition = part.headers.get(b'Content-Disposition', b'').decode()
                            if 'filename=' in disposition:
                                filename = disposition.split('filename=')[1].strip('"')
                                img_path = os.path.join(IMAGE_DIR, filename)
                                with open(img_path, 'wb') as f:
                                    f.write(part.content)
                                print(f"Saved image to {img_path}")
                    except Exception as e:
                        print(f"Multipart parsing failed: {e}")

            # 연결 종료
            conn.close()