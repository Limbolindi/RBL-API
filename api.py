#!/usr/bin/python3
import json
import uuid
import atexit
from flask import Flask, request

pi = None
DEBUG = False
if DEBUG:
    import api_debug_classes
    pi = api_debug_classes.pigpio()
else:
    import pigpio
    pi = pigpio.pi()


API_LED_PIN = {}
API_PIN = {}
CONFIG = {}

app = Flask(__name__)


def __ini__():
    f = open("config.json", "r")
    api_config = json.load(f)
    global API_PIN
    API_PIN = api_config.get("API_PIN", []).values()
    global API_LED_PIN
    API_LED_PIN = api_config.get("API_LED_PIN", {})
    global pi
    for i in API_PIN:
        pi.set_mode(int(i), pigpio.OUTPUT)
    for i in API_LED_PIN:
        for v in ("R", "G", "B"):
            pi.set_mode(API_LED_PIN[i][v], pigpio.OUTPUT)

    fi = open("app_config.json", "r")
    app_config = json.load(fi)
    for i in range(0, app_config["variables"].__len__()):
        if app_config["variables"][i]["id"] == "36766584-0dbc-4c68-865b-9ebbd7c481c2":
            for key, value in api_config.get("API_PIN", {}).items():
                tmp_key = {"label": key, "value": value, "id": str(uuid.uuid4())}
                app_config["variables"][i]["options"].append(tmp_key)
    for i in range(0, app_config["variables"].__len__()):
        if app_config["variables"][i]["id"] == "cfbe5b89-3c85-4dc4-952b-64bd73e32d58":
            for key, value in api_config.get("LED_Name", {}).items():
                tmp_key = {"label": key, "value": value, "id": str(uuid.uuid4())}
                app_config["variables"][i]["options"].append(tmp_key)
    global CONFIG
    CONFIG = app_config


def pin_read(pin):
    return pi.read(pin)


def pin_write(pin, state):
    pi.write(pin, state)


def led_write(led, val_R, val_G, val_B):
    pi.set_PWM_dutycycle(API_LED_PIN[led]["R"], val_R)
    pi.set_PWM_dutycycle(API_LED_PIN[led]["G"], val_G)
    pi.set_PWM_dutycycle(API_LED_PIN[led]["B"], val_B)


@app.route("/setled", methods=["POST"])
def post_set_led():
    data = request.get_json()
    if data.get('pin', None) is None:
        return "", 202
    if data.get('RGB', None) is None:
        return "", 202
    if data.get('pin') not in API_LED_PIN:
        return "", 203
    r = int(data.get('RGB')[0:2], 16)
    g = int(data.get('RGB')[2:4], 16)
    b = int(data.get('RGB')[4:6], 16)
    led_write(data.get('pin'), r, g, b)
    return "", 200


@app.route("/setpin", methods=["POST"])
def post__set_pin():
    data = request.get_json()
    if data.get('pin', None) is None:
        return "", 202
    if data.get('state', None) is None:
        return "", 202
    if data.get('pin') not in API_PIN:
        return "", 202
    pin_write(data.get('pin'), data.get('state'))
    return "", 200


@app.route("/getpin", methods=["POST"])
def post__get_pin():
    data = request.get_json()
    if data.get('pin', None) is None:
        return "", 202
    #######################
    return pin_read(data.get('pin')), 200


@app.route("/config", methods=["GET"])
def get__config():
    return CONFIG, 200


@app.route("/off", methods=["POST"])
def post_off():
    for i in API_PIN:
        pin_write(i, 0)
    for i in API_LED_PIN:
        led_write(i,0,0,0)
    return "", 200


def closedown():
    pi.stop()


atexit.register(closedown)

if __name__ == "__main__":
    __ini__()
    app.debug = DEBUG
    app.run(host='0.0.0.0')

