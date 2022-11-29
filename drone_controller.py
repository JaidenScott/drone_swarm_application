from flask import Flask, render_template, request, redirect, url_for
from Model.models import DroneModel, db
from flask_sqlalchemy import SQLAlchemy
from djitellopy.swarm import TelloSwarm
from djitellopy import Tello
import time

"""
Name: Jaiden Scott
Student ID: 20063526
"""

"""
This is a drone swarm application that uses flask. You create a sequence of commands for a list of drones.
Drones can be added and deleted. The battery for each of the drones will update when the drones are connected.
"""
tello = Tello()

URL = "redis://default:redispw@172.20.20.99:49153"
# on application start create worker using .\venv\Scripts\celery.exe -A drone_controller.celery_app_name worker
# celery = Celery('tasks', broker=URL)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///drone_DB.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

drone_commands = []

db.init_app(app)


@app.route('/', methods=["POST","GET"])
def index():
    """
    The main page of the flask application
    """
    drone_list = DroneModel.query.all()

    print(drone_list)
    return render_template('index.html', drone_list=drone_list, drone_commands=drone_commands)


@app.before_first_request
def create_table():
    """
    This function will create all the tables in the models
    """
    db.create_all()


@app.route('/add_drone', methods=["POST","GET"])
def add_drone():
    """
    The page for adding the drones in the flask application
    """
    if request.method == 'GET':
        return render_template('add_drone.html')
    if request.method == 'POST':
        drone = DroneModel(request.form.get("id"), request.form.get("name"), request.form.get("ip"))
        db.session.add(drone)
        db.session.commit()
        return redirect(url_for("index"))


@app.route('/delete_drone', methods=["POST", "GET"])
def delete_drone():
    """
    The page for deleting the drones in the flask application
    """
    if request.method == 'GET':
        return render_template("delete_drone.html")
    if request.method == 'POST':
        id = request.form.get("ID")
        drone = DroneModel.query.filter_by(drone_id=id).first()
        if drone is not None:
            db.session.delete(drone)
            db.session.commit()
        return redirect(url_for("index"))


def update_drones_telemetry(drone_list, battery_list):
    """
    This function will update the battery for the drones in the drones database
    """
    index = 0
    for i in drone_list:
        drone = DroneModel.query.filter_by(drone_id=i.drone_id).first()
        drone.drone_battery = battery_list[index]
        db.session.commit()
        index += 1


@app.route('/move_left')
def move_left():
    """
    This function will add a left command and refresh the page
    """
    drone_commands.append("left")
    return redirect(url_for("index"))


@app.route('/move_right')
def move_right():
    """
    This function will add a right command and refresh the page
    """
    drone_commands.append("right")
    return redirect(url_for("index"))


@app.route('/move_forward')
def move_forward():
    """
    This function will add a forward command and refresh the page
    """
    drone_commands.append("forward")
    return redirect(url_for("index"))


@app.route('/clear_all_commands')
def clear_all_commands():
    """
    This function will clear all the commands
    """
    drone_commands.clear()
    return redirect(url_for("index"))


@app.route('/start_operation')
def start_operation():
    """
    This function will call the function that will begin going through the commands
    """
    operate_drones()
    return redirect(url_for("index"))


def operate_drones():
    """
    This function will create a swarm using the IP's, then it will send the sequence of commands to all of the drones.
    """
    drone_ips = []
    drone_batteries = []
    drone_list = DroneModel.query.all()

    for i in drone_list:
        # Take the IP's from the database and add them to the list
        drone_ips.append(i.drone_ip)

    if len(drone_ips) != 0:
        # If there is no drone IP's then dont connect
        swarm = TelloSwarm.fromIps(drone_ips)
        swarm.connect()
        drone_batteries.clear()
        for i in swarm:
            # Whether there is or no commands. This will always store the drones battery
            battery = i.get_battery()
            drone_batteries.append(battery)
        update_drones_telemetry(drone_list, drone_batteries)

        if len(drone_commands) != 0:
            # If there is drone commands then initiate drone take-off
            swarm.takeoff()
            for i in drone_commands:
                print(i)
                if i == "left":
                    swarm.move_left(100)
                    time.sleep(1)
                if i == "right":
                    swarm.move_right(100)
                    time.sleep(1)
                if i == "forward":
                    swarm.move_forward(100)
                    time.sleep(1)
            swarm.land()

            swarm.end()


if __name__ == '__main__':
    app.run()
