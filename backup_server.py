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


class Server():

    def __init__(self, request=None):

        '''
        @Params:
        responseHeader: the header variable that send back in response
        responseContet: the content that send back in response
        statusCode: the code and message will be used in response
        httpVersion: the http version used for server
        requestMethod: only get method will be handled
        '''
        self.request = request
        self.responseHeader = ""
        self.responseMessage = ""
        self.statusCode = {200:"OK",
                    301:"MOVED PERMANTLY",
                    404:"NOT FOUND",
                    405:"METHOD NOT ALLOWED"}
        self.httpVersion = "HTTP/1.1"
        self.requestMethod = ["GET"]
        self.key_type = "Content-Type"
        self.key_length = "Content-Length"
        self.value_html = "text/html"
        self.value_css = "text/css"
        self.not_found_msg = '''
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

    def set_status_code(self, code):

        # Format of status in response: "HTTP_version status_code msg\r\n"
        status_pattern = "{} {} {}\r\n"
        msg = self.statusCode[code]
        self.responseHeader += status_pattern.format(self.httpVersion, str(code), msg)

        # Debug use 
        print("Response status: " + status_pattern.format(self.httpVersion, str(code), msg))
    
    def set_header(self, key, value):

        # Format of header: "Key: Value\r\n"
        header_pattern = "{}: {}\r\n"
        self.responseHeader += header_pattern.format(key, value)

        #Debug use
        # print("Response header: " + header_pattern.format(key, value))

    def set_path(self, url):

        # Init path, serve files in './www/'
        path = os.curdir + "/www" + url
        print("PATH: {}, URL: {}".format(path,url))
        path = path.replace("www/www", "www")
        print(os.path.isdir(path))

        # Check if path ending with '/'
        if os.path.isdir(path):
            if path[-1] != '/':
                url += '/'
                # print("REDIRECT:   " + url)
                self.set_status_code(301)
                self.responseHeader += "Location: {}\r\n".format(url)
                return None
        
        # If path is a valid path, add index.html to path
        if os.path.isdir(path):
            path += "index.html"

        # Normalize path
        # Reference: https://docs.python.org/3.3/library/os.path.html?highlight=path
        newPath = os.path.normcase(path)
        # Remove redundant separators
        newPath = os.path.normpath(newPath)

        return newPath

    def get_content(self, file_path=None):

        # If file_path is None, the file is not valid and response 404 not found 
        if file_path == None:
            self.set_header(self.key_type, self.value_html)
            return self.not_found_msg
        
        # Get extension of file
        # Reference: https://stackoverflow.com/questions/541390/extracting-extension-from-filename-in-python
        file_type = os.path.splitext(file_path)[1]

        # Set header for response based on corresponding type of file
        if 'html' in file_type:
            self.set_header(self.key_type, self.value_html)
        if 'css' in file_type:
            self.set_header(self.key_type, self.value_css)

        # Add length of file in bytes at field 'Content-Length'
        # Reference: https://docs.python.org/3/library/stat.html
        status = os.stat(file_path)
        self.set_header(self.key_length, str(status.st_size))

        # Read content from file
        with open(file_path, "r") as file:
            file_content = file.read()

        return file_content

    def process_request(self):

        try:
            request_data = self.request.decode('utf-8')
        except UnicodeDecodeError:
            print("Cannot decode.")

        # Split by '\r\n' to get the request method & URL
        request_line = request_data.split("\r\n")[0].split(" ")
        print(request_line)
        request_method = request_line[0]
        request_url = ""
        if len(request_line) > 1:
            request_url = request_line[1]

        # Check if method is Get, if not, response 405
        if "GET" not in request_method:
            self.set_status_code(405)
            self.responseMessage = "{}\r\n".format(self.responseHeader)
            return
        
        # Check path by calling set_path
        newPath = self.set_path(request_url)
        file_content = None
        if newPath == None:
            self.responseMessage = "{}\r\n{}".format(self.responseHeader, file_content)
            return 

        # Set content
        if os.path.isfile(newPath):
            self.set_status_code(200)
            file_content = self.get_content(newPath)
        else:
            self.set_status_code(404)
            file_content = self.get_content()
        self.responseMessage = "{}\r\n{}".format(self.responseHeader, file_content)

    def get_response_msg(self):
        return self.responseMessage

    def set_request(self, request):
        self.request = request


class MyWebServer(socketserver.BaseRequestHandler):
    


    def handle(self):
        self.data = self.request.recv(1024).strip()
        # print ("Got a request of: %s\n" % self.data)
        # self.request.sendall(bytearray("OK",'utf-8'))
        baseServer = Server(self.data)
        baseServer.process_request()
        response_msg = baseServer.get_response_msg()
        
        if response_msg == None:
            return
        self.request.sendall(response_msg.encode('utf-8'))

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
