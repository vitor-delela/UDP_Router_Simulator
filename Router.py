import socket
import time
import re
import threading

# Current router IP address and port
host_ip_address = "10.132.241.200"
host_port = 5000
filename = 'NeighborsIP.txt'

# Initial Routing table 
routing_table = []
neighborsList = []
seconds = []

# Create UDP socket
socket_router = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Associate socket and IP address to router port
socket_router.bind((host_ip_address, host_port))

print("Server started...\n")

def initSecondsArray():
    #seconds: each array contains the IP Address and the last updated time
    for route in routing_table:
        seconds.append([route["destination"], time.time()])

def updateNeighborsList():
    with open(filename, 'r') as neighborsFile:
        for neighbor in neighborsFile:
            neighborsList.append(neighbor.strip())
            updateRoutingTable(neighbor.strip(), 0, neighbor.strip()) # Setting routing table with neighbors

def convertRoutingTableToProtocol():
    #protocol e.g. *192.168.0.1;4
    if routing_table:
        message = ""
        for route in routing_table:
            message += "*"
            message+=route["destination"]
            message+=";"
            message+=str(route["metric"])
        return message
    return '!'

def updateRoutingTable(destination, metric, output):
    found = False
    tableWasUpdated = False

    #update existing route in routing table 
    for route in routing_table:
        if route["destination"] == destination:
            found = True
            for opt in seconds:
                if opt[0] == destination:
                    opt[1] = time.time() #update last updated time
            if int(route["metric"]) > int(metric)+1:
                route["metric"] = int(metric)+1 #update metric if new metric is smaller than existing one
                route["output"] = output
                tableWasUpdated = True

    #add new route to routing table
    if (not found and (destination != host_ip_address)):
        routing_table.append({"destination": destination, "metric": int(metric)+1, "output": output})
        seconds.append([destination, time.time()])
        tableWasUpdated = True
    
    return tableWasUpdated

def decodeMessage(message, address):
    #protocol:
    # ! = new neighbor
    # *192.168.1.2;1*192.168.1.3;1 = IP 192.168.1.2 Metric 1 + IP 192.168.1.3 Metric 1

    tableWasUpdated = False

    if message == "!":
        print(f"New neighbor detected [{address[0]}].")
        newneighborAddress = str(address[0])

        if newneighborAddress.strip() not in neighborsList:
            neighborsList.append(newneighborAddress.strip())
            #start registering time for new neighbor
            seconds.append([newneighborAddress, time.time()])

    else:
        regex = "\*[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+;[0-9]+"
        routes = re.findall(regex, message) #find all groups of routes received -> ip & metric together

        if routes:
            for route in routes: #iterate over every group of route
                print("Received route:", route)

                routeRegex = "\*(.*);(.*)" #regex to split ip and metric
                splittedRoute = re.match(routeRegex, route)

                if splittedRoute:
                    ipAddress = splittedRoute.group(1)
                    metric = splittedRoute.group(2)

                    tableWasUpdated = updateRoutingTable(ipAddress, metric, address[0])
                else:    
                    print("\nNot the expected format: ", route)
        
    return tableWasUpdated

def printRoutingTable():
    print("\nRouting Table:")
    print("Destination\t\t\tMetric\t\tOutput")
    for item in routing_table:
        print(item["destination"], "\t\t\t", item["metric"], "\t\t", item["output"])
    print()

def sendMessageToneighbors():
    #convert current routing table to protocol and send to all neighbors
    for ng in neighborsList:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(10)
        try:
            s.sendto(convertRoutingTableToProtocol().encode(), (ng, host_port))
        except ConnectionRefusedError:
            print("Connection refused to neighbor", ng)
        except TimeoutError:
            print("Connection timed out to neighbor", ng)
        except Exception as e:
            print(f"Error occurred: {str(e)}")
        finally:
            s.close()

def removeInactiveRoutes():
    #to be run as a thread
    #every route not received again in 30 seconds might be deleted, which means the neighbors are not sending it anymore, and it probably left the network
    while True:
        for output in seconds:
            if (time.time() - output[1]) >= 30:
                for route in routing_table:
                    if route["destination"] == output[0]:
                        routing_table.remove(route)
                        seconds.remove(output)
        #time.sleep(10)

def receiveMessages():
    #to be run as a thread
    while True:
        message, address = socket_router.recvfrom(1024)
        message = message.decode()

        if decodeMessage(message, address): #true means the table was update with the received message, then it is required to send the new table to neighbors
            sendMessageToneighbors()
            print("[Table was updated]")

        printRoutingTable()

        print("New message to be sent to neighborsList: ", convertRoutingTableToProtocol())

def sendMessages():
    #to be run as a thread
    while True:
        printRoutingTable()
        sendMessageToneighbors() #send routing table to neighbors every 10 seconds
        time.sleep(10)

# -------------------------------

updateNeighborsList()

thread_receive = threading.Thread(target=receiveMessages)
thread_send = threading.Thread(target=sendMessages)
thread_inactives = threading.Thread(target=removeInactiveRoutes)

thread_receive.start()
thread_send.start()
initSecondsArray()
thread_inactives.start()

