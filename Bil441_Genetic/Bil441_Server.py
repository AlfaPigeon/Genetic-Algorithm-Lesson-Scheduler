from http.server import HTTPServer, BaseHTTPRequestHandler




class requestHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        if(self.path == "/" or self.path == "/index"):
            try:
                page = open("Bil441_Genetic/index.html").read()
                page = page.replace("@i","<button onclick=\"alert(\'I LOVE YOU ANIL\')\">HEY H EY HEY</button>")
                self.send_response(200)
            except:
                page = "<b>"+"We all love Bil 441"+"</b>"
                self.send_response(404)

        self.send_header('content-type', 'text/html')
        self.end_headers()

        self.wfile.write(bytes(page, 'utf-8'))





def main():
    address = ('localhost', 8080)
    server = HTTPServer(address, requestHandler)
    server.serve_forever()


if __name__ == "__main__":
    main()