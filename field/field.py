from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

field = None
under_control_minos = dict()

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
    return jsonify(field.to_dict())

@app.route('/minos', methods=['POST'])
def new_mino():
    color_id = request.json.get('colorId')
    obj_coords = request.json.get('coordinates')
    mino_id = len(under_control_minos)

    x0 = int(field.width / 2)
    y0 = 3
    coords = list()
    for i in obj_coords:
        col = x0 + i['x']
        row = y0 - i['y']
        coords.append({'row': row, 'col': col})
    if not field.is_collision(coords):
        mino = Mino(mino_id, x0, y0, coords, color_id)
        under_control_minos[str(mino_id)] = mino
        field.set_object(coords, color_id)
        return jsonify(mino.to_dict()), 201
    else:
        return jsonify({'message': 'collision'})


@app.route('/minos', methods=['GET'])
def get_minos():
    res = dict()
    for k, v in under_control_minos.items():
        res[k] = v.to_dict()

    return jsonify(res)

@app.route('/minos/<int:mino_id>', methods=['GET'])
def get_mino_by_id(mino_id):
    mino = under_control_minos[str(mino_id)]
    return jsonify(mino.to_dict())

@app.route('/minos/<int:mino_id>', methods=['PUT'])
def update_mino_by_id(mino_id):
    op = request.json.get('operation')
    if op == "down":
        result = under_control_minos[str(mino_id)].move(op='down')
    elif op == "left":
        result = under_control_minos[str(mino_id)].move(op='left')
    elif op == "right":
        result = under_control_minos[str(mino_id)].move(op='right')
    else:
        return jsonify({'message': 'invalid operation'}), 400
    
    if result is not None:
        return jsonify(result)
    else:
        return jsonify({'message': 'collision'})


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

class Mino:
    def __init__(self, mino_id, x, y, coords, color_id):
        self.id = mino_id
        self.x = x                  # origin x
        self.y = y                  # origin y
        self.coords = coords        # coordinates of blocs (absolute)
        self.color_id = color_id

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

#    def rotate(self):
#        new_coords_relative = list()
#        for i in self.coords_relative:
#            cood = dict()           


    def to_dict(self):
        res = dict()
        res['id'] = self.id
        res['coords'] = self.coords
        res['colorId'] = self.color_id
        return res


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
