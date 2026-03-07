from textual_serve.server import Server

server = Server("python app.py", host="0.0.0.0", port=5000)
server.serve()
