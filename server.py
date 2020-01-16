#  coding: utf-8 
import socketserver
import os.path

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    

    '''
    @Params:
    responseHeader: the header variable that send back in response
    responseContet: the content that send back in response
    statusCode: the code and message will be used in response
    httpVersion: the http version used for server
    requestMethod: only get method will be handled
    '''
    responseHeader = ""
    responseContent = ""
    statusCode = {200:"OK",
                    301:"MOVED PERMANTLY",
                    404:"NOT FOUND",
                    405:"METHOD NOT ALLOWED"}
    httpVersion = "HTTP/1.1"
    requestMethod = "GET"
    not_found_msg = '''
                <!DOCTYPE html>
                <html>
                <head>
                        <meta http-equiv="Content-Type"
                        content="text/html;charset=utf-8"/>
                </head>

                <body>
                <h1>404</h1>
                <h2>Page Not Found</h2>
	            </body>
                </html> 
                    '''

    '''
    @Help functions:

    '''

    def set_status_code(self, code):
        
        # Format of status in response: "HTTP_version status_code msg\r\n"
        status_pattern = "{} {} {}\r\n" 
        msg = self.statusCode[code]
        self.responseHeader += status_pattern.format(self.httpVersion, str(code), msg)

        #Debug use
        print("Response status: " + status_pattern.format(self.httpVersion, str(code), msg))
        
    def set_header(self, key, value):

        # Format of header: "Key: Value\r\n"
        header_pattern = "{}: {}\r\n"
        self.responseHeader += header_pattern.format(key, value)

        #Debug use
        print("Response header: " + header_pattern.format(key, value))

    def get_content(self, file_path):
        
        # Content-Type, the only key we used for this assignment
        key = "Content-Type"

        # Get extension of file
        # Reference: https://stackoverflow.com/questions/541390/extracting-extension-from-filename-in-python
        file_type = os.path.splitext(file_path)[1]

        if 'html' in file_type:
            self.set_header(key, "text/html")
        
        if 'css' in file_type:
            self.set_header(key, "text/css")

        with open(file_path, "r") as file:
            file_content = file.read()

        return file_content

    def set_path(self, url):

        # Init path where index.html and base.css is
        path = os.curdir + "/www/"


    def process_request(self, request_data):

        # Parameter 'request_data' is the request received from client
        try:
            request_data = request_data.decode('utf-8')
        except UnicodeDecodeError:
            print("Cannot decode.")

        # Split by '\r\n\' to get the request method & URL
        request_line = request_data.split("\r\n")[0].split(" ")
        request_method = request_line[0]
        request_url = request_line[1]

        # Check if method is GET, if not, report to client cannot handle
        if "GET" not in request_method:
            self.set_status_code(405)
            return

        self.set_path(request_url)



    def handle(self):
        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s\n" % self.data)
        self.request.sendall(bytearray("OK",'utf-8'))

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
