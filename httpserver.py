#! /usr/bin/env python3
# HTTP Server
# Nicholas Stewart
# ID: 31512469
# Section: 008
import sys
import socket
import os
import time


# Create a dummy HTML file to test outputs
def createHTML(Name):
    try:
        HTMLDoc = open(Name, 'x')
        HTMLDoc.write("<html><p>First Line<br />Second Line<br />Third Line<br />COMPLETE<p><html>")
        HTMLDoc.close()
        print("HTML File Generated")
    except FileExistsError:
        print("HTML File exists")


# gets and updates Last modified time in the serverCache dictionary
def getMTime(Name):
    secs = os.path.getmtime(Name)
    t = time.gmtime(secs)
    last_mod_time = time.strftime("%a, %d %b %Y %H:%M:%S GMT\r\n", t)
    return last_mod_time


def convertToSec(gmtTime):
    t = time.strptime(gmtTime, "%a, %d %b %Y %H:%M:%S %Z\r\n")
    secs = time.mktime(t)
    return secs


def getCurTime():
    curTime = time.strftime("%a, %d %b %Y %I:%M:%S", time.gmtime())
    curTime = curTime + " GMT" + "\r\n"
    # print(curTime)
    return curTime


createHTML("filename.html")

# Find all .html files in our current directory and add them to a cache data structure
serverCache = {}
dir_path = os.path.dirname(os.path.realpath(__file__))

for root, dirs, files in os.walk(dir_path):
    for file in files:
        if file.endswith('.html'):
            serverCache[str(file)] = getMTime(str(file))
# print(serverCache)


# Read server IP address and port from command-line arguments
serverIP = sys.argv[1]
serverPort = int(sys.argv[2])
dataLen = 1000000
# Create a TCP "welcoming" socket. Notice the use of SOCK_STREAM for TCP packets
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Assign IP address and port number to socket
serverSocket.bind((serverIP, serverPort))
# Listen for incoming connection requests
serverSocket.listen(1)

print('The server is ready to receive on port:  ' + str(serverPort) + '\n')

# loop forever listening for incoming connection requests on "welcoming" socket
while True:
    # Accept incoming connection requests; allocate a new socket for data communication
    connectionSocket, address = serverSocket.accept()
    print("Socket created for client " + address[0] + ", " + str(address[1]))

    # Receive and print the client data in bytes from "data" socket
    data = connectionSocket.recv(dataLen).decode()
    print("Data from client: " + data)

    # Break apart message
    data = data.split("\r\n")
    headerInfo = data[1:]
    # This should look at all header fields and check for If-Modified-Since
    ConditionalFlag = 0
    for element in headerInfo:
        if element == '':
            headerInfo.remove(element)
        else:
            HeaderField = element.split(":")
            if "If-Modified-Since" in HeaderField:
                ConditionalFlag = 1

    fileName = data[0].split()
    fileName = fileName[1]
    fileName = fileName[1:]
    if fileName not in serverCache:
        # Respond with a file not found error
        date = getCurTime()
        response = "HTTP/1.1 404 Not Found\r\n" + "Date: " + date + "Content-Length: 0\r\n" + "\r\n"
        connectionSocket.send(response.encode())
    # Evaluate Get/Cond get and create needed info (check modified time against 1. Cache(update if needed) 2. ifModTime)
    elif ConditionalFlag == 1:
        # Conditional Get
        ifModTime = data[2].strip("If-Modified-Since:")
        ifModTime = ifModTime.strip()
        ifModTime = ifModTime + "\r\n"
        ifModSec = convertToSec(ifModTime)
        lastMod = getMTime(fileName)

        # Update server cache
        if serverCache[fileName] != lastMod:
            serverCache[fileName] = lastMod

        # Compare Modified Times
        lastModSec = convertToSec(lastMod)
        if ifModSec < lastModSec:
            # File has been modified since specified time Send Full get response
            f = open(fileName, 'r')
            content = f.read()
            contentLen = len(content.encode())
            date = getCurTime()
            response = "HTTP/1.1 200 OK\r\n" + "Date: " + date + "Last-Modified: " + lastMod + "Content-Length: " + str(contentLen) + "\r\n" + "Content-Type: text/html; charset=UTF-8\r\n" + "\r\n" + content
            connectionSocket.send(response.encode())
        else:
            # File has NOT been modified
            date = getCurTime()
            response = "HTTP/1.1 304 Not Modified\r\n" + "Date: " + date + "\r\n"
            connectionSocket.send(response.encode())
    elif ConditionalFlag == 0:
        lastMod = getMTime(fileName)
        f = open(fileName, 'r')
        content = f.read()
        contentLen = len(content.encode())
        date = getCurTime()
        response = "HTTP/1.1 200 OK\r\n" + "Date: " + date + "Last-Modified: " + lastMod + "Content-Length: " + str(contentLen) + "\r\n" + "Content-Type: text/html; charset=UTF-8\r\n" + "\r\n" + content
        connectionSocket.send(response.encode())
    else:
        print("unrecognized command")
