# run me, and then execute
#      ngrok.exe http 5000
# in command terminal
# Or, deploy me on aws lambda
#     zappa update
#
# Refer to https://www.youtube.com/watch?v=zsYjS-lca3M
#
import logging
import json
from flask import Flask, render_template
from flask_ask import Ask, statement, question, session
from spyrk import SparkCloud
# PARTICLE_DEVICE_ID = 'YOUR_DEVICE_ID_HERE'
# PARTICLE_ACCESS_TOKEN = 'YOUR_ACCESS_TOKEN_HERE'
# PARTICLE_NODE_MAIN = YOUR_MAIN_NODE_ID
# or
from config import PARTICLE_DEVICE_ID, PARTICLE_ACCESS_TOKEN, PARTICLE_NODE_MAIN, PARTICLE_NODE_KM
from colormaker import name2wrgb


app = Flask(__name__)
ask = Ask(app, "/")
spark = SparkCloud(PARTICLE_ACCESS_TOKEN)
logging.getLogger("flask_ask").setLevel(logging.DEBUG)
sparkDevice = spark.devices[PARTICLE_DEVICE_ID]


@ask.launch
def hello():
    logging.info("Hello Xlight")
    if sparkDevice.connected:
        speech_text = render_template('hello')
        return question(speech_text).reprompt(speech_text).simple_card('HelloXlight', speech_text)
    else:
        speech_text = render_template('device_offline')
        return question(speech_text).reprompt(speech_text).simple_card('HelloXlight', speech_text)

@ask.intent('AMAZON.HelpIntent')
def help():
    speech_text = render_template('help')
    return question(speech_text).reprompt(speech_text).simple_card('HelloXlight', speech_text)


@ask.intent("XlightStateIntent")
def set_state(state):
    if sparkDevice.connected:
        speech_text = render_template('state_changed', state=state)
        # Call cloud function
        cmd_obj = {
            'cmd': 1,
            'nd': PARTICLE_NODE_MAIN,
            'state': 1 if state.lower() == 'on' else 0
        }
        cmd_string = json.dumps(cmd_obj)
        sparkDevice.JSONCommand(cmd_string)
    else:
        speech_text = render_template('device_offline')
    return statement(speech_text).simple_card('HelloXlight', speech_text)


@ask.intent("XlightColorIntent")
def set_color(color):
    if sparkDevice.connected:
        speech_text = render_template('color_changed', color=color)
        # Call cloud function
        cmd_obj = dict(cmd=2, nd=PARTICLE_NODE_MAIN)
        cmd_obj['ring'] = [0, 1, 80] + name2wrgb(color)
        cmd_string = json.dumps(cmd_obj)
        sparkDevice.JSONCommand(cmd_string)
    else:
        speech_text = render_template('device_offline')
    return statement(speech_text).simple_card('HelloXlight', speech_text)


@ask.intent("XlightBrightnessIntent", convert={'brightness': int})
def set_brightness(brightness):
    if sparkDevice.connected:
        if (brightness > 100) or (brightness < 0):
            speech_text = render_template('error_brightness')
        else:
            speech_text = render_template('brightness_changed', brightness=brightness)
            # Call cloud function
            cmd_obj = dict(cmd=3, nd=PARTICLE_NODE_MAIN, value=brightness)
            cmd_string = json.dumps(cmd_obj)
            sparkDevice.JSONCommand(cmd_string)
    else:
        speech_text = render_template('device_offline')
    return statement(speech_text).simple_card('HelloXlight', speech_text)


@ask.intent("XlightDimmerIntent")
def set_dimmer(dimmer):
    speech_text = render_template('dimmer_changed', dimmer=dimmer)
    # ToDo: change with relative value, or according to current status (got from status event)
    return statement(speech_text).simple_card('HelloXlight', speech_text)


@ask.intent("XlightSpecialEffectIntent")
def set_specialeffect(effect):
    if effect == 'special effect':
        speech_text = render_template('help_specialeffect')
        return question(speech_text).reprompt(speech_text).simple_card('HelloXlight', speech_text)
    elif sparkDevice.connected:
        speech_text = render_template('effect_changed', effect=effect)
        # Call cloud function
        cmd_obj = dict(cmd=7, nd=PARTICLE_NODE_MAIN)
        lower_effect = effect.lower()
        if lower_effect == 'breathing':
            cmd_obj['filter'] = 1
        elif lower_effect == 'fast breathing':
            cmd_obj['filter'] = 2
        elif lower_effect == 'slow dancing':
            cmd_obj['filter'] = 3
        elif lower_effect == 'dancing':
            cmd_obj['filter'] = 4
        else:
            cmd_obj['filter'] = 0
        cmd_string = json.dumps(cmd_obj)
        sparkDevice.JSONCommand(cmd_string)
    else:
        speech_text = render_template('device_offline')
    return statement(speech_text).simple_card('HelloXlight', speech_text)


@ask.intent("XlightChristmasIntent")
def set_x_state(state):
    if sparkDevice.connected:
        speech_text = render_template('x_state_changed', state=state)
        # Call cloud function
        cmd_obj = {
            'cmd': 8,
            'nd': PARTICLE_NODE_KM,
            'msg': 1,
            'ack': 1,
            'tag': 65 if state.lower() == 'on' else 66,
            'pl': '1'
        }
        cmd_string = json.dumps(cmd_obj)
        sparkDevice.JSONCommand(cmd_string)
    else:
        speech_text = render_template('device_offline')
    return statement(speech_text).simple_card('HelloXlight', speech_text)


@ask.session_ended
def session_ended():
    return "{}", 200


if __name__ == '__main__':
    app.run(debug=True)

