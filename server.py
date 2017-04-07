import web
import socketserver

##
#WEB server
#

PORT = 8000

#Handler = http.server.SimpleHTTPRequestHandler
Handler = web.testHTTPRequestHandler

httpd = socketserver.TCPServer(("", PORT), Handler)
print("serving at port", PORT)
httpd.serve_forever()
