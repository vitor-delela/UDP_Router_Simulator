# UDP_Router_Simulator
Router instance simulator using UDP connection

Initially, the IP addresses of neighbors routers must be informed in the application so that several different topologies can be simulated. This is made through a text file located at the same folder as the app. The IP addresses must be informed on the file. Each neighbor router is an instance of the implemented router running on another physical machine. 

Three fields must be present in the routing table: Destination IP, Metric and Output IP.

Routing tables (Destination, IP, and Metric fields only) are sent to neighbors routers every 10 seconds. Upon receiving the routing table from its neighbors, the application checks the routes received and makes the necessary updates to the local routing table, in order to maintain always the shortest path to every IP. 

In case a router leaves the network at any time and its neighbors are no longer receiving route messages, the routes will be forgotten after 30 seconds without  messages received.

**Comunication Protocol**

|     **IP**     |**Metric**|   **Output**   |
|----------------|----------|----------------|
|   192.168.1.2  |     1    |   192.168.1.1  |
|   192.168.1.3  |     1    |   192.168.1.1  |

_Message that will be sent:_
*192.168.1.2;1*192.168.1.3;1

