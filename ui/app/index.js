const express = require('express');
const fs = require('fs');
const request = require('request');

const app = express();
app.use(express.static('web'));
app.use(express.json())

app.get('/colors', (req, res) => {
        const colors = JSON.parse(fs.readFileSync('./colors.json', 'utf8'));
        res.json(colors);
});

app.post('/colors', (req, res) => {
        var colors = JSON.parse(fs.readFileSync('./colors.json', 'utf8'));
        const id = Object.keys(colors).length;
        const color = req.body.color;

        const colorItem = {
                "id": id,
                "color": color
        }

        colors[String(id)] = color;
        colors = JSON.stringify(colors);
        fs.writeFileSync('colors.json', colors);

        console.log('Add: ' + JSON.stringify(colorItem));

        res.json(colorItem);
});

app.get('/field', (req, res) => {
        request.get({
                uri: 'http://field/field',
                headers: {'Content-type': 'application/json'},
                json: true
        }, function(err, rq, data){
                res.json(data);
        })
});

app.listen(80, () => console.log('Listening on port 80'));
