var colorMap;

async function fetchColorMap() {
        return fetch('/colors')
                .then((response) => response.json())
                .then((json) => {
                        colorMap = json;
                })
}

async function fetchField() {
        return fetch('/field')
                .then((response) => response.json())
                .then((field) => {
                        draw(field);
                })
}

function draw(json) {
  const BLOCK_SIZE = 20;
  const WALL_SIZE = 3;
  var canvas = document.getElementById("stage");
  canvas.setAttribute("width", String(json.width * BLOCK_SIZE + WALL_SIZE*2));
  canvas.setAttribute("height", String(json.height * BLOCK_SIZE + WALL_SIZE));

  var ctx = canvas.getContext("2d");

  ctx.beginPath();
  ctx.strokeStyle = "rgb(220, 220, 220)";
  ctx.lineWidth = 1;

  for (let i = 0; i < json.height + 1; i++) {
      ctx.moveTo(WALL_SIZE, i * BLOCK_SIZE);
      ctx.lineTo(WALL_SIZE + json.width * BLOCK_SIZE, i * BLOCK_SIZE);
  }
  for (let j = 0; j < json.width + 1; j++) {
      ctx.moveTo(WALL_SIZE + j * BLOCK_SIZE, 0);
      ctx.lineTo(WALL_SIZE + j * BLOCK_SIZE, json.height * BLOCK_SIZE);
  }
  ctx.stroke();
  ctx.closePath();

  ctx.beginPath();
  //ctx.strokeStyle = "black";
  ctx.fillStyle = "black";
  ctx.fillRect(0, 0, WALL_SIZE, json.height * BLOCK_SIZE + WALL_SIZE)
  ctx.fillRect(WALL_SIZE + json.width * BLOCK_SIZE, 0, WALL_SIZE, json.height * BLOCK_SIZE + WALL_SIZE)
  ctx.fillRect(0, json.height * BLOCK_SIZE, json.width * BLOCK_SIZE + WALL_SIZE*2, WALL_SIZE)
  //ctx.lineWidth = 5;
  //ctx.moveTo(0, 0);
  //ctx.lineTo(0, json.height*20);
  //ctx.moveTo(json.width*20, 0);
  //ctx.lineTo(json.width*20, json.height*20);
  //ctx.moveTo(0, json.height*20);
  //ctx.lineTo(json.width*20, json.height*20);
  ctx.stroke();
  ctx.closePath();

  for (let i = 0; i < json.height; i++) {
    for (let j = 0; j < json.width; j++) {
      if (json.data[i][j] != 0) {
        color = colorMap[String(json.data[i][j])]
        ctx.fillStyle = color;
        ctx.fillRect(WALL_SIZE + j * BLOCK_SIZE, i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE);

        ctx.beginPath();
        ctx.strokeStyle = "black";
        ctx.lineWidth = 1;
        ctx.rect(WALL_SIZE + j * BLOCK_SIZE, i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE);
        ctx.stroke();
        ctx.closePath();
      }
    }
  }
}

fetchColorMap();
setInterval(fetchField, 1000);
