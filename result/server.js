const express = require('express');
const http = require('http');
const path = require('path');
const { Pool } = require('pg');
const { Server } = require('socket.io');

const app = express();
const server = http.createServer(app);
const io = new Server(server);

const port = process.env.PORT || 5001;

const pool = new Pool({
  connectionString: process.env.DATABASE_URL || 'postgres://postgres:postgres@db:5432/postgres'
});

app.get('/health', (req, res) => {
  res.status(200).send('OK');
});

app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'views', 'index.html'));
});

async function getVotes() {
  try {
    const result = await pool.query('SELECT vote, COUNT(id) AS count FROM votes GROUP BY vote');
    const votes = { a: 0, b: 0 };
    result.rows.forEach((row) => {
      if (row.vote === 'a') votes.a = parseInt(row.count, 10);
      if (row.vote === 'b') votes.b = parseInt(row.count, 10);
    });
    return votes;
  } catch (err) {
    console.error('Error fetching votes:', err);
    return { a: 0, b: 0 };
  }
}

io.on('connection', async (socket) => {
  const votes = await getVotes();
  socket.emit('scores', votes);
});

setInterval(async () => {
  const votes = await getVotes();
  io.emit('scores', votes);
}, 1000);

server.listen(port, () => {
  console.log(`Result app listening on port ${port}`);
});
