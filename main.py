from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
from pathlib import Path
import mimetypes
import json
import logging
from threading import Thread
import socket
from datetime import datetime
import os

BASE_DIR = Path()
BUFFER_SIZE = 1024
HTTP_PORT = 3000
HTTP_HOST = '0.0.0.0'
SOCKET_PORT = 5000
SOCKET_HOST = '127.0.0.1'


class MyHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        route = urllib.parse.urlparse(self.path)
        if route.path == '/':
            self.send_html('index.html')
        elif route.path == '/message':
            self.send_html('message.html')
        else:
            file = BASE_DIR.joinpath(route.path[1:])
            if file.exists():
                self.send_static(file)
            else:
                self.send_html('error.html', status_code=404)

    def do_POST(self):
        size = self.headers.get('Content-Length')
        data = self.rfile.read(int(size))
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_socket.sendto(data, (SOCKET_HOST, SOCKET_PORT))
        client_socket.close()
        self.send_response(302)
        self.send_header(keyword='Location', value='/message')
        self.end_headers()

    def send_html(self, filename, status_code=200):
        self.send_response(status_code)
        self.send_header(keyword='Content-Type', value='text/html')
        self.end_headers()
        with open(filename, 'rb') as file:
            self.wfile.write(file.read())

    def send_static(self, filename, status_code=200):
        self.send_response(status_code)
        mime_type, *_ = mimetypes.guess_type(filename)
        if mime_type:
            self.send_header(keyword='Content-Type', value=mime_type)
        else:
            self.send_header(keyword='Content-Type', value='text/plain')
        self.end_headers()
        with open(filename, 'rb') as file:
            self.wfile.write(file.read())


def save_data_from_form(data):
    parse_data = urllib.parse.unquote_plus(data.decode())
    try:
        parse_dict_message = {key: value for key, value in [el.split('=') for el in parse_data.split('&')]}

        with open('storage/data.json', 'r', encoding='utf-8') as file:
            path = Path('storage/data.json')
            if path.stat().st_size == 0: #check if file is empty
                parse_dict_time = {str(datetime.now()): parse_dict_message}
            else:
                parse_dict_time = json.load(file)
                parse_dict_time[str(datetime.now())] = parse_dict_message

        with open('storage/data.json', 'w', encoding='utf-8') as file:
            json.dump(parse_dict_time, file, ensure_ascii=False, indent=4)

    except ValueError as val_err:
        logging.error(val_err)
    except OSError as os_err:
        logging.error(os_err)


def run_socket_server(host, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((host, port))
    logging.info('Starting socket server')
    try:
        while True:
            message, address = server_socket.recvfrom(BUFFER_SIZE)
            logging.info(f'Socked received {address}:{message}')
            save_data_from_form(message)
    except KeyboardInterrupt:
        pass
    finally:
        server_socket.close()


def run_http_server(host, port):
    address = (host, port)
    http_server = HTTPServer(address, MyHTTPRequestHandler)
    logging.info('Starting http server')
    try:
        http_server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        http_server.server_close()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(threadName)s %(message)s')

    server = Thread(target=run_http_server, args=(HTTP_HOST, HTTP_PORT))
    server.start()

    server_socket = Thread(target=run_socket_server, args=(SOCKET_HOST, SOCKET_PORT))
    server_socket.start()