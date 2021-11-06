from flask import Flask, request, jsonify
from flask_cors import CORS
import logging

app = Flask(__name__)
CORS(app)

LOGFILE_NAME = "flask.log"
app.logger.setLevel(logging.DEBUG)
log_handler = logging.FileHandler(LOGFILE_NAME)
log_handler.setLevel(logging.DEBUG)
app.logger.addHandler(log_handler)


field = None

@app.route('/field', methods=['GET'])
def get_field():
    if field is None:
        res = dict()
    else:
        res = field.to_dict()

    return jsonify(res)

@app.route('/field', methods=['POST'])
def create_field():
    global field
    width = request.json.get('width')
    height = request.json.get('height')
    #field_id = str(len(fields) + 1)
    field = Field(width, height)
    #fields[field_id] = field
    return jsonify(field.to_dict()), 201

@app.route('/collision', methods=['POST'])
def is_collision():
    coords = request.json.get('coords')
    result = field.is_collision(coords)
    resp = dist()
    resp["result"] = result
    return jsonify(resp)

@app.route('/set', methods=['POST'])
def set_object():
    resp = dict()
    coords = request.json.get('coords')
    color_id = request.json.get('color_id')
    if field.is_collision(coords):
        resp["result"] = "failed"
        resp["message"] = "collision"
    else:
        field.set_object(coords, color_id)
        resp["result"] = "success"
    return jsonify(resp)

@app.route('/move', methods=['POST'])
def move_object():
    app.logger.debug("start /move")
    resp = dict()
    coords_from = request.json.get('coords_from')
    coords_to = request.json.get('coords_to')
    color_id = request.json.get('color_id')
    field.unset_object(coords_from)
    if field.is_collision(coords_to):
        field.set_object(coords_from, color_id)
        resp["result"] = "failed"
        resp["message"] = "collision"
    else:
        field.set_object(coords_to, color_id)
        resp["result"] = "success"
    app.logger.debug("end /move")
    return jsonify(resp)

@app.route('/drop', methods=['POST'])
def drop_object():
    resp = dict()
    coords_from = request.json.get('coords')
    color_id = request.json.get('color_id')

    field.unset_object(coords_from)
    while True:
        coords_to = list()
        for i in coords_from:
            coord = dict()
            coord['row'] = i['row'] + 1
            coord['col'] = i['col']
            coords_to.append(coord)
          
        if field.is_collision(coords_to):
            coords_to = coords_from
            break
        else:
            coords_from = coords_to

    field.set_object(coords_to, color_id)
    resp["result"] = "success"
    resp["message"] = coords_to
    app.logger.debug("end /move")
    return jsonify(resp)

class Field:

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.data = self.init_field_data(width, height)
        self.minos = dict()

    def init_field_data(self, width, height):
        data = list()
        for i in range(height):
            #if i != height - 1:
            #    column = [1 if j == 0 or j == width - 1 else 0 for j in range(width)]
            #else:
            #    column = [1 for j in range(width)]
            column = [0 for j in range(width)]
            data.append(column)
        return data

    def set_object(self, coords, color_id):
        for i in coords:
            row = i['row']
            col = i['col']
            self.data[row][col] = color_id

    def unset_object(self, coords):
        for i in coords:
            row = i['row']
            col = i['col']
            self.data[row][col] = 0


    def is_collision(self, coords):
        for i in coords:
            row = i['row']
            col = i['col']
            if row < 0 or row > self.height - 1:
                return True
            if col < 0 or col > self.width - 1:
                return True
            if self.data[row][col] != 0:
                return True

        return False

    def to_dict(self):
        res = dict()
        #res['id'] = self.id
        res['width'] = self.width
        res['height'] = self.height
        res['data'] = self.data
        return res


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, threaded=False)
