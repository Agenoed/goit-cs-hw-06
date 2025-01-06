import http.server
import socketserver
import socket
import threading
import json
import urllib.parse
from datetime import datetime

HOST = "0.0.0.0"
HTTP_PORT = 3000
SOCKET_HOST = "socket_server"
SOCKET_PORT = 5000

class HTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        print(f"Request path: {self.path}")

        if self.path == "/":
            self.send_file("/app/index.html")
        elif self.path == "/message.html":
            self.send_file("/app/message.html")
        elif self.path == "/style.css":
            self.send_file("/app/style.css")
        elif self.path == "/logo.png":
            self.send_file("/app/logo.png")
        else:
            self.send_error(404, "File not found")

    def do_POST(self):
        if self.path == "/message.html":
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length).decode()

            form_data = urllib.parse.parse_qs(post_data)
            username = form_data.get("username", [""])[0]
            message = form_data.get("message", [""])[0]

            send_data_to_socket_server(username, message)

            self.send_response(303)
            self.send_header("Location", "/")
            self.end_headers()
        else:
            self.send_error(404, "File not found")

    def send_error(self, code, message):
        print(f"Sending error: {code} {message}")
        if code == 404:
            try:
                with open("/app/error.html", "rb") as f:
                    self.send_response(404)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(f.read())
            except FileNotFoundError:
                self.send_response(500)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(b"Internal Server Error")
        else:
            self.send_response(code)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(message.encode())

    def send_file(self, filepath):
        try:
            with open(filepath, "rb") as f:
                content = f.read()
                self.send_response(200)
                if filepath.endswith(".html"):
                    self.send_header("Content-type", "text/html")
                elif filepath.endswith(".css"):
                    self.send_header("Content-type", "text/css")
                elif filepath.endswith(".png"):
                    self.send_header("Content-type", "image/png")
                self.end_headers()
                self.wfile.write(content)
        except FileNotFoundError:
            self.send_error(404, "File not found")


def send_data_to_socket_server(username, message):
    data = {"username": username, "message": message}
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((SOCKET_HOST, SOCKET_PORT))
        s.sendall(json.dumps(data).encode())

def run_http_server():
    with socketserver.TCPServer((HOST, HTTP_PORT), HTTPRequestHandler) as httpd:
        print(f"HTTP server started on port {HTTP_PORT}")
        httpd.serve_forever()

if __name__ == "__main__":
    http_thread = threading.Thread(target=run_http_server)
    http_thread.start()