const path = require('path');
const express = require('express');
const async = require('async');
const { Pool } = require('pg');
const cookieParser = require('cookie-parser');
const http = require('http');
const socketIo = require('socket.io');

const app = express();
const server = http.Server(app);
const io = socketIo(server);

const port = process.env.PORT || 8080;

const postgresHost =
  process.env.POSTGRES_HOST || 'db';

const postgresUser =
  process.env.POSTGRES_USER || 'postgres';

const postgresPassword =
  process.env.POSTGRES_PASSWORD;

const postgresDatabase =
  process.env.POSTGRES_DB || 'postgres';

if (!postgresPassword) {
  throw new Error(
    'POSTGRES_PASSWORD environment variable is required.'
  );
}

const pool = new Pool({
  host: postgresHost,
  user: postgresUser,
  password: postgresPassword,
  database: postgresDatabase,
  port: 5432
});

io.on('connection', (socket) => {
  socket.emit('message', {
    text: 'Welcome!'
  });

  socket.on('subscribe', (data) => {
    socket.join(data.channel);
  });
});

async.retry(
  {
    times: 1000,
    interval: 1000
  },
  (callback) => {
    pool.connect((err, client, done) => {
      if (err) {
        console.error('Waiting for PostgreSQL');
        callback(err);
        return;
      }

      console.log(
        `Connected to PostgreSQL at ${postgresHost}`
      );

      callback(null, {
        client,
        done
      });
    });
  },
  (err, connection) => {
    if (err) {
      console.error('Giving up on PostgreSQL connection');
      return;
    }

    getVotes(
      connection.client,
      connection.done
    );
  }
);

function getVotes(client, done) {
  const query = `
    SELECT
      vote,
      COUNT(*) AS count
    FROM votes
    GROUP BY vote;
  `;

  client.query(query, [], (err, result) => {
    if (err) {
      console.error(
        `Error performing query: ${err.message}`
      );
    } else {
      const votes =
        collectVotesFromResult(result);

      io.sockets.emit(
        'scores',
        JSON.stringify(votes)
      );
    }

    setTimeout(
      () => getVotes(client, done),
      1000
    );
  });
}

function collectVotesFromResult(result) {
  const votes = {
    a: 0,
    b: 0
  };

  result.rows.forEach((row) => {
    votes[row.vote] =
      parseInt(row.count, 10);
  });

  return votes;
}

app.use(cookieParser());

app.use(
  express.urlencoded({
    extended: false
  })
);

app.use(
  express.static(
    path.join(__dirname, 'views')
  )
);

app.get('/', (req, res) => {
  res.sendFile(
    path.resolve(
      __dirname,
      'views',
      'index.html'
    )
  );
});

app.get('/health', async (req, res) => {
  try {
    await pool.query('SELECT 1');

    res.status(200).json({
      status: 'ok'
    });
  } catch {
    res.status(503).json({
      status: 'unhealthy'
    });
  }
});

server.listen(port, () => {
  console.log(
    `Result service running on port ${port}`
  );
});
