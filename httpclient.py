#! /usr/bin/env python3
# HTTP Client
# Nicholas Stewart
# ID: 31512469
# Section: 008
import sys
import socket


# function to check if the cache.txt file exists
def cacheCheck():
    try:
        Ccache = open("clientCache.txt", 'x')
        Ccache.close()
        print("Cache File Generated")
    except FileExistsError:
        print("Cache File exists")


def HTTPGET():
    print("File not cached, Commencing HTTP GET")
    # Create GET request
    getReq = "GET /" + getFile + " HTTP/1.1" + "\r\n" + "Host: " + host + ":" + str(port) + "\r\n" + "\r\n"

    # Create TCP connection to server
    print("Connecting to " + host + ", " + str(port))
    clientSocket.connect((host, port))

    # Send encoded data through TCP connection
    print("Sending HTTP GET request to server: ")
    print(getReq)
    clientSocket.send(getReq.encode())

    # Receive the server response
    dataEcho = clientSocket.recv(1000000)

    # Display the decoded server response as an output
    print("Received data from server: " + dataEcho.decode())

    # break apart message
    dataEcho = dataEcho.decode()
    message = dataEcho.split("\r\n")
    content = message[-1]
    statusFlag = 0
    status = message[0]
    status = status.split()
    if status[1] == "404":
        statusFlag = 1
    if statusFlag == 0:
        for element in message:
            headerFinder = element.split(":")
            if "Last-Modified" in headerFinder:
                date = element.strip("Last-Modified: ")
                date = date.strip()
        # Cache received data(name-body-lastModified)
        Ccache = open("clientCache.txt", "r+")
        newLines = Ccache.readlines()
        Ccache.close()
        Ccache = open("clientCache.txt", "w")
        for line in newLines:
            Ccache.write(line + "\n")
        Ccache.write(getFile + "-" + content + "-" + date)


def HTTPCONDGET(lastModified):
    print("File cached, Commencing HTTP Conditional GET")

    # Create GET request
    getReq = "GET /" + getFile + " HTTP/1.1" + "\r\n" + "Host: " + host + ":" + str(port) + "\r\n" + "If-Modified-Since: " + lastModified + "\r\n" + "\r\n"

    # Create TCP connection to server
    print("Connecting to " + host + ", " + str(port))
    clientSocket.connect((host, port))

    # Send encoded data through TCP connection
    print("Sending HTTP Conditional GET request to server: ")
    print(getReq)
    clientSocket.send(getReq.encode())

    # Receive the server response
    dataEcho = clientSocket.recv(1000000)

    # Display the decoded server response as an output
    print("Received data from server:")
    print(dataEcho.decode())
    dataEcho = dataEcho.decode()
    message = dataEcho.split("\r\n")
    statusFlag = 0
    status = message[0]
    status = status.split()
    if status[1] == "404":
        statusFlag = 1
    content = message[-1]
    modFlag = 0
    for element in message:
        headerFinder = element.split(":")
        if "Last-Modified" in headerFinder:
            date = element.strip("Last-Modified: ")
            date = date.strip()
            modFlag = 1
    # Cache received data if file was modified(name-body-lastModified)
    if modFlag == 1 and statusFlag == 0:
        Ccache = open("clientCache.txt", "r+")
        cacheInfo = Ccache.readlines()
        for cachedFile in cacheInfo:
            fileInfo = cachedFile.split("-")
            if getFile in fileInfo:
                Ccache.close()
                Ccache = open("clientCache.txt", "r+")
                oldFile = cachedFile
                newFile = getFile + "-" + content + "-" + date
                data = Ccache.read()
                data = data.replace(oldFile, newFile)
                Ccache.close()
                Ccache = open("clientCache.txt", "w")
                Ccache.write(data)


# Get the server hostname, port and data length as command line arguments
argument = sys.argv[1]
split1 = argument.split(":")
host = split1[0]
split2 = split1[1].split("/")
port = int(split2[0])
getFile = split2[1]

# Create TCP client socket. Note the use of SOCK_STREAM for TCP packet
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Check to see if cache.txt exits. If not create the cache file
cacheCheck()

# Check cache for html object and do appropriate request function
cacheInfo = {}
cache = open("clientCache.txt", "r+")
contents = cache.readlines()

if not contents:
    HTTPGET()
for line in contents:
    infoTuple = line.split("-")
    objName = infoTuple[0]
    lastModified = infoTuple[2]
    cacheInfo[objName] = lastModified
if getFile in cacheInfo and contents:
    HTTPCONDGET(cacheInfo[getFile])
elif getFile not in cacheInfo and contents:
    HTTPGET()

# Close the client socket
clientSocket.close()