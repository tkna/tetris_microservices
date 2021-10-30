from flask import Flask, jsonify
from flask_cors import CORS
import json, requests
import random

app = Flask(__name__)
CORS(app)

instances = dict()

@app.route('/minos')
def minos():
    with open('minos.json') as f:
        jsn = json.load(f)

    return jsonify(jsn)

@app.route('/instances', methods=['POST'])
def create_instance():
    with open('minos.json') as f:
        minos_json = json.load(f)

    field = get_field()

    mino_object = random.choice(minos_json)
    instance_id = len(instances)

    x0 = int(field["width"] / 2)
    y0 = 3
    instance = MinoInstance(instance_id, mino_object, x0, y0)
    
    res = instance.set_to_field()
    if res["result"] == "success":
        instances[str(instance_id)] = instance
        return jsonify(instance.to_dict()), 201
    elif res["result"] == "failed":
        if res["message"] == "collision":
            return jsonify(res)

def get_field():
    res = requests.get('http://field/field')
    return res.json()

class MinoInstance:
    def __init__(self, instance_id, obj, x, y):
        self.id = instance_id
        self.mino_id = obj["id"]
        self.x = x                  # origin x
        self.y = y                  # origin y

        coords_abs = list()
        for i in obj["coords"]:
            col = x + i['x']
            row = y - i['y']
            coords_abs.append({'row': row, 'col': col})
        self.coords = coords_abs        # coordinates of blocs (absolute)
        self.color_id = obj["color_id"]

    def is_collision(self):
        body = self.coords
        res = requests.post('http://field/collision', json=body)
        return res.json()["result"]

    def set_to_field(self):
        body = {"coords": self.coords, "color_id": self.color_id}
        res = requests.post('http://field/set', json=body)
        return res.json()

    def to_dict(self):
        res = dict()
        res['id'] = self.id
        res['mino_id'] = self.mino_id
        res['x'] = self.x
        res['y'] = self.y
        res['coords'] = self.coords
        res['colorId'] = self.color_id
        return res

"""
    def move(self, op):
        if op == 'down':
            x_new = self.x
            y_new = self.y + 1
        elif op == 'left':
            x_new = self.x - 1
            y_new = self.y
        elif op == 'right':
            x_new = self.x + 1
            y_new = self.y

        new_coords = list()
        for i in self.coords:
            cood = dict()
            if op == 'down':
                cood['row'] = i['row'] + 1
                cood['col'] = i['col']
            elif op == 'left':
                cood['row'] = i['row']
                cood['col'] = i['col'] - 1
            elif op == 'right':
                cood['row'] = i['row']
                cood['col'] = i['col'] + 1
            new_coords.append(cood)

        field.unset_object(self.coords)
        if field.is_collision(new_coords):
            print("collision")
            field.set_object(self.coords, self.color_id)
            return None
        else:
            self.x = x_new
            self.y = y_new
            self.coords = new_coords
            field.set_object(self.coords, self.color_id)
            return self.to_dict()

    def rotate(self):
        app.logger.debug("x: {}, y: {}".format(self.x, self.y))

        new_coords = list()
        for i in self.coords:
            cood = dict()
            x_relative = i['col'] - self.x
            y_relative = self.y - i['row']
            cood['col'] = self.x - y_relative   # minus y_relative because of 90 degree counter-clockwise
            cood['row'] = self.y - x_relative   # minus x_relative because the coordinate system is upside down in the field
            app.logger.debug("x_relative: {}, y_relative: {}".format(x_relative, y_relative))
            app.logger.debug("col: {}, row: {}".format(cood['col'], cood['row']))
            new_coords.append(cood)

        field.unset_object(self.coords)
        if field.is_collision(new_coords):
            print("collision")
            field.set_object(self.coords, self.color_id)
            return None
        else:
            self.coords = new_coords
            field.set_object(self.coords, self.color_id)
            return self.to_dict()      
"""

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
