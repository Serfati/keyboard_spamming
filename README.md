#   👑 Keyboard Spamming Battle Royale  ⌨ 

<img src="https://in.bgu.ac.il/marketing/graphics/BGU.sig3-he-en-white.png" height="48px" align="right" /> 
<img src="https://steamuserimages-a.akamaihd.net/ugc/911293473580328863/DCB12F76423E5226064ABC302B326C2F527A42DF/" height="200" style=" border: 5px solid #555;"/> 

  

# Description  

Your objective is to write a client-server application which will implement a fast-paced Keyboard
Spamming game. The players in this game are randomly divided into two teams, which have ten
seconds to mash as many keys on the keyboard as possible.
Each team in the course will write both a client application and a server application, and
everybody’s clients and servers are expected to work together with full compatibility.

# Suggested Architecture 

The client is a single-threaded app, which has three states:
● Looking for a server. You leave this state when you get an offer message.
● Connecting to a server. You leave this state when you successfully connect using TCP
● Game mode - collect characters and from the keyboard and send them over TCP. collect
data from the network and print it onscreen.
Note that in game mode the client responds to two events - both keyboard presses and data
coming in over TCP. Think about how you can do this.
The server is multi-threaded since it has to manage multiple clients. It has two states:
● Waiting for clients - sending out offer messages and responding to request messages
and new TCP connections. You leave this state after 10 seconds.
● Game mode - collect characters from the network and calculate the score. You leave this
state after 10 seconds.


# Packet Formats 

● Servers broadcast their announcements with destination port 13117 using UDP. There is
one packet format used for all UDP communications:
○ Magic cookie (4 bytes): 0xfeedbeef. The message is rejected if it doesn’t start
with this cookie
○ Message type (1 byte): 0x2 for offer. No other message types are supported.
○ Server port (2 bytes): The port on the server that the client is supposed to
connect to over TCP (the IP address of the server is the same for the UDP and
TCP connections, so it doesn't need to be sent).
The data over TCP has no packet format. After connecting, the client sends the
predefined team name to the server, followed by a line break (‘\n’). After that, the client
simply prints anything it gets from the server onscreen, and sends anything it gets from
the keyboard to the server.

## ⚠️ Prerequisites  
  
- [Python 3.6](https://www.python.org/download/releases/3.6/)  
- [Git 2.26](https://git-scm.com/downloads/)  
- [PyCharm IDEA](https://www.jetbrains.com/pycharm/) (recommend)  

## 📦 How To Install  
  
You can modify or contribute to this project by following the steps below:  
  
**1. Clone the repository**  
  
- Open terminal ( <kbd>Ctrl</kbd> + <kbd>Alt</kbd> + <kbd>T</kbd> )  
  
- [Clone](https://help.github.com/en/github/creating-cloning-and-archiving-repositories/cloning-a-repository) to a location on your machine.  
 ```bash  
 # Clone the repository 
 $> git clone https://github.com/serfati/bibi.git  

 # Navigate to the directory 
 $> cd bibi
  ``` 

**2. Install Dependencies**  
  
 ```bash  
 # install with requirments
 $> ./setup.sh
 ```  

**3. launch of the server**  
  
 ```bash  
 # Run Server 
 $> python3 server.py
 ```  

 **4. launch of the client**  
  
 ```bash  
 # Run Client 
 $> python3 client.py
 ```  

 **5. enjoy**  

---  

> author Serfati
  
## ⚖️ License  
  
This program is free software: you can redistribute it and/or modify it under the terms of the **MIT LICENSE** as published by the Free Software Foundation.  
  
**[⬆ back to top](#description)**