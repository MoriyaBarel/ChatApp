# Chat App Project

## Introduction

In this project we were required to implement online chat room, based on networking. It allows different users to communicate with each other using a shared Server.
Communication between the users is carried out by either sending private messages or broadcast all.
In Addition the server provides the option to request download files.
All the data is transferred using TCP protocol except the files that are transferred through RDT over UDP(reliable data transfer using UDP).


## Reliable data transfer using UDP
Reliable data transfer using UDP (User Datagram Protocol) for file transfer is a client-server application. Our implementation for reliability over UDP is achieved using Selective Repeat(SR) protocol. UDP, unlike TCP (Transmission Control Protocol), is an unreliable, connectionless data transfer protocol existing in the transport layer of TCP/IP architecture. One of the primary purposes of this project is to download a file from a server using RDT over UDP.

Selective Repeat Protocol(SRP) is also connectionless protocol. Server parallelly sends a certain number of packets for each new request from the client. Each packet consists a sequence number for identification. Once receiving the packets from the server, clients verify the sequence of the received packets. Upon verifying, the client can know about the missing packets – if there are any. The client sends a request for those missing packets and repeats the process until all the packets for a particular request are received. Otherwise, it requests for the fresh set of packets from the server.

* Overcoming packet loss:
Using our implementation of RDT over UDP, When experiencing packet loss the client sends all the sequence numbers of the missing packets to the server. The server,in response to the client's acknowledge message sends the missing packets accordinglly .The process will only be completed when all packets are received and the file has been download successfully.

* Overcoming latency:
whenever we use 50% packet loss or more (aka low latency mode) there's a scenario in which a client tries to request a file from the server and whenever the server is asking for the missing packets the client might send the same message twice causing the string that represents the missing packets to be written one to many times causing a key error.
our solution to this problem is : 
We use a function that splits the sequence numbers recieved and make sure that there no duplicates and no sequence number was chained together with another sequence number (e.g 0102 splits to 01,02).



## Diagram

![diagram](https://i.imgur.com/kKivxpu.png)

## How to run

first of all ,to run the project please make sure you have the following installed:
Thread , socket , tkinter.

second we'll find the ip of the server we want to connect to , 
run the next command in the command line: "ipconfig".
we will take the ip feild :
![ipv4](https://i.imgur.com/81UVOyK.png)

**Application guide**:

**Server**

* download the server .
  
* go to cmd and cd to the server path than run the next command: python server.py 
 
 ![server](https://user-images.githubusercontent.com/92746221/156893475-cfdc8681-9bdf-4032-8f15-fa7e8481a004.png)



**client**

* download the client . 



* go to cmd and cd to the client path than run the next command:
 client.py server_ip  
For example:

![clientpng](https://user-images.githubusercontent.com/92746221/156893518-9f53173b-9adf-4f53-822f-f95dc9e85a39.png)

later , the next screen will appear : 

![first](https://user-images.githubusercontent.com/92746221/156894086-7a4e0164-212a-47cb-a5b8-3804569b480d.png)


The chat supports the following actions:

* #getusers

 After using the command(or click the button), the user will receive all the connected users . 
 
![onlineusers](https://user-images.githubusercontent.com/92746221/156894413-4c1bcd86-db79-4df1-818b-2b6b4fb98f3e.png)

* #getfilelist 

 After using the command(or click the button), the user will receive the file list . 
 
![filelist](https://user-images.githubusercontent.com/92746221/156894584-ae5f2825-2f96-4f72-a0a4-e3f7cdc56004.png)

* !request 

After using this command(or click the button), the user can download a file . 

![request](https://user-images.githubusercontent.com/92746221/156894826-b18f55b7-dd95-42e0-a3d4-24b16a2513c9.png)

**examples**:
![image](https://user-images.githubusercontent.com/92746221/156895037-3292bc32-f2f3-4c83-a930-21dd3535c906.png)


short video : 

https://user-images.githubusercontent.com/92746221/156895266-0d4be2d4-dd12-4350-b6a3-d871a2a7e735.mp4
