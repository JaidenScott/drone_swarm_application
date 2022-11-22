![](static/logo2.png)

Drone Swarm Application
-----------------------

This app allows you to create a swarm of drones to connect to and
control, all at the same time. This app will let create a sequence
of commands that you can send when you click the start operation button.
If there are no drones in the swarm then it will do nothing. The drones 
will also return their battery info as long as the drones are connected.

I used flask to create the user interface, flask-SQLAlchemy to create a 
database to store the drone info and the TelloSwarm library from djitellopy to
connect and control the drone swarm

Required libraries
------------------
These are the libraries that need to be installed to properly run this application
- Flask
- Flask-SQLAlchemy
- Djitellopy

Flask
-----
Api Documentation - https://flask.palletsprojects.com/en/2.2.x/

Flask-SQLAlchemy
----------------
Api Documentation - https://flask-sqlalchemy.palletsprojects.com/en/3.0.x/

Djitellopy
----------
M4GNV5 github - https://github.com/damiafuentes/DJITelloPy