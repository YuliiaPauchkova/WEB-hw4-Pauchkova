from flask import Flask, render_template, request, redirect, url_for
import socket
import json
from datetime import datetime
import threading
import os

app = Flask(__name__)

# Маршрути для сторінок
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/message', methods=['GET', 'POST'])
def message():
    if request.method == 'POST':
        username = request.form['username']
        message = request.form['message']
        
        # Відправка даних на Socket сервер через UDP
        send_message_to_socket(username, message)

        return redirect(url_for('index'))  # Перенаправлення на головну сторінку після відправки повідомлення
    return render_template('message.html')

# Обробка помилки 404
@app.errorhandler(404)
def page_not_found(error):
    return render_template('error.html'), 404

# Конфігурація для Socket сервера
UDP_HOST = '127.0.0.1'
UDP_PORT = 5000

# Функція для відправлення даних на Socket сервер через UDP
def send_message_to_socket(username, message):
    try:
        data = {
            'username': username,
            'message': message
        }
        data_string = json.dumps(data).encode()

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:
            client_socket.sendto(data_string, (UDP_HOST, UDP_PORT))
    except Exception as e:
        print('Помилка під час відправлення даних на Socket сервер:', e)

# Функція для запуску Socket сервера в окремому потоці
def run_socket_server():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
            server_socket.bind((UDP_HOST, UDP_PORT))
            print('UDP сервер слухає на {}:{}'.format(UDP_HOST, UDP_PORT))

            while True:
                data, addr = server_socket.recvfrom(1024)
                print('Отримано від {}: {}'.format(addr, data.decode()))

                # Розбір отриманих даних та збереження у файлі data.json
                try:
                    data_dict = json.loads(data.decode())
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
                    data_dict['timestamp'] = timestamp

                    storage_dir = 'storage'
                    if not os.path.exists(storage_dir):
                        os.makedirs(storage_dir)

                    with open(os.path.join(storage_dir, 'data.json'), 'a') as f:
                        json.dump(data_dict, f)
                        f.write('\n')
                except Exception as e:
                    print('Помилка під час обробки даних:', e)
    except Exception as e:
        print('Помилка під час запуску Socket сервера:', e)

# Запуск HTTP сервера та Socket сервера
if __name__ == '__main__':
    # Запускаємо Socket сервер у окремому потоці
    socket_thread = threading.Thread(target=run_socket_server)
    socket_thread.start()

    # Запускаємо HTTP сервер
    app.run(debug=True, port=3000)