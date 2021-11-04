from flask import Flask, request, jsonify
from flask_cors import CORS
import json, requests
import random
import logging

app = Flask(__name__)
CORS(app)
app.logger.setLevel(logging.DEBUG)

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
        res["instance"] = instance.to_dict()
        return jsonify(res), 201
    elif res["result"] == "failed":
        if res["message"] == "collision":
            return jsonify(res)

@app.route('/instances/<int:instance_id>', methods=['PUT'])
def move_instance(instance_id):
    op = request.json.get('operation')
    if op == "down":
        result = instances[str(instance_id)].move(op='down')
        if result["result"] != "success":
            del instances[str(instance_id)]
    elif op == "left":
        result = instances[str(instance_id)].move(op='left')
    elif op == "right":
        result = instances[str(instance_id)].move(op='right')
    elif op == "rotate":
        result = instances[str(instance_id)].rotate()
    else:
        return jsonify({'message': 'invalid operation'}), 400
    
    return jsonify(result)

def get_field():
    res = requests.get('http://field/field')
    return res.json()

class MinoInstance:
    def __init__(self, instance_id, obj, x, y):
        self.id = instance_id
        self.mino_id = obj["id"]
        self.x = x                  # origin x
        self.y = y                  # origin y
        self.coords = obj["coords"] # coordinates of blocks (relative)
        self.color_id = obj["color_id"]

    def abs_coords(self):
        coords_abs = list()
        for i in self.coords:
            col = self.x + i['x']
            row = self.y - i['y']
            coords_abs.append({'row': row, 'col': col})
        return coords_abs

    def get_abs_coords(self, x, y, coords):
        coords_abs = list()
        for i in coords:
            col = x + i['x']
            row = y - i['y']
            coords_abs.append({'row': row, 'col': col})
        return coords_abs

    def is_collision(self):
        body = self.abs_coords()
        res = requests.post('http://field/collision', json=body)
        return res.json()["result"]

    def set_to_field(self):
        body = {"coords": self.abs_coords(), "color_id": self.color_id}
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
        
        coords_abs_new = self.get_abs_coords(x_new, y_new, self.coords)

        body = {"coords_from": self.abs_coords(), "coords_to": coords_abs_new, "color_id": self.color_id}
        res = requests.post('http://field/move', json=body)
        res = res.json()

        if res["result"] == "success":
            self.x = x_new
            self.y = y_new

        return res

    def rotate(self):
        coords_new = list()
        for i in self.coords:
            cood = dict()
            cood['x'] = -i['y']
            cood['y'] = i['x']
            coords_new.append(cood)

        coords_abs_new = self.get_abs_coords(self.x, self.y, coords_new)
        body = {"coords_from": self.abs_coords(), "coords_to": coords_abs_new, "color_id": self.color_id}
        res = requests.post('http://field/move', json=body)
        res = res.json()

        if res["result"] == "success":
            self.coords = coords_new
    
        return res  


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
