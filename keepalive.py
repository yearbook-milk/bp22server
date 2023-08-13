import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

class handler(BaseHTTPRequestHandler):
  def do_GET(self):
      self.send_response(200)
      self.send_header('Content-type', 'text/plain')
      self.end_headers()
      msg = f'HELLO!'
      self.wfile.write(bytes(str(msg), 'utf-8'))

class thread(threading.Thread):
    def __init__(self, thread_name, thread_ID):
        threading.Thread.__init__(self)
        self.thread_name = thread_name
        self.thread_ID = thread_ID

    def run(self, port):
      from http.server import BaseHTTPRequestHandler, HTTPServer
      with HTTPServer(('', port), handler) as server:
        print('Server started.')
        server.serve_forever()