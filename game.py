import streamlit as st

st.title('🐍 Snake Game')

# HTML and JavaScript code for the Snake game
html_code = '''
<html>
<head>
  <style>
    body { margin: 0; }
    canvas { display: block; background: #000; }
  </style>
</head>
<body>
  <canvas id="gameCanvas" width="400" height="400"></canvas>
  <script>
    var canvas = document.getElementById("gameCanvas");
    var ctx = canvas.getContext("2d");
    var grid = 16;
    var count = 0;
    var snake = {
      x: 160,
      y: 160,
      dx: grid,
      dy: 0,
      cells: [],
      maxCells: 4
    };
    var apple = {
      x: 320,
      y: 320
    };
    function getRandomInt(min, max) {
      return Math.floor(Math.random() * (max - min)) + min;
    }
    document.addEventListener('keydown', function(e) {
      // Prevent snake from reversing
      if (e.keyCode === 37 && snake.dx === 0) { // Left arrow
        snake.dx = -grid;
        snake.dy = 0;
      } else if (e.keyCode === 38 && snake.dy === 0) { // Up arrow
        snake.dy = -grid;
        snake.dx = 0;
      } else if (e.keyCode === 39 && snake.dx === 0) { // Right arrow
        snake.dx = grid;
        snake.dy = 0;
      } else if (e.keyCode === 40 && snake.dy === 0) { // Down arrow
        snake.dy = grid;
        snake.dx = 0;
      }
    });
    function loop() {
      requestAnimationFrame(loop);
      if (++count < 4) {
        return;
      }
      count = 0;
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      snake.x += snake.dx;
      snake.y += snake.dy;
      // Wrap snake position on edge of screen
      if (snake.x < 0) {
        snake.x = canvas.width - grid;
      } else if (snake.x >= canvas.width) {
        snake.x = 0;
      }
      if (snake.y < 0) {
        snake.y = canvas.height - grid;
      } else if (snake.y >= canvas.height) {
        snake.y = 0;
      }
      // Keep track of snake cells
      snake.cells.unshift({ x: snake.x, y: snake.y });
      if (snake.cells.length > snake.maxCells) {
        snake.cells.pop();
      }
      // Draw apple
      ctx.fillStyle = 'red';
      ctx.fillRect(apple.x, apple.y, grid - 1, grid - 1);
      // Draw snake
      ctx.fillStyle = 'lime';
      snake.cells.forEach(function(cell, index) {
        ctx.fillRect(cell.x, cell.y, grid - 1, grid - 1);
        // Snake ate apple
        if (cell.x === apple.x && cell.y === apple.y) {
          snake.maxCells++;
          apple.x = getRandomInt(0, 25) * grid;
          apple.y = getRandomInt(0, 25) * grid;
        }
        // Check collision with all cells after this one
        for (var i = index + 1; i < snake.cells.length; i++) {
          // Snake occupies same space as a body part. Reset game
          if (cell.x === snake.cells[i].x && cell.y === snake.cells[i].y) {
            snake.x = 160;
            snake.y = 160;
            snake.cells = [];
            snake.maxCells = 4;
            snake.dx = grid;
            snake.dy = 0;
            apple.x = getRandomInt(0, 25) * grid;
            apple.y = getRandomInt(0, 25) * grid;
          }
        }
      });
    }
    requestAnimationFrame(loop);
  </script>
</body>
</html>
'''

# Embed the game into the Streamlit app
st.components.v1.html(html_code, height=400)
