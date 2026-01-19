const express = require('express');
const path = require('path');
const http = require('http');

const app = express();
app.use(express.json());

// Serve static files FIRST (before proxy)
app.use('/static', express.static(path.join(__dirname, 'staticfiles')));
app.use('/media', express.static(path.join(__dirname, 'media')));

// Handle /proxy/8000 prefix for static files
app.use((req, res, next) => {
  if (req.path.startsWith('/proxy/8000/static')) {
    req.url = req.url.replace('/proxy/8000', '');
    return express.static(path.join(__dirname, 'staticfiles'))(req, res, next);
  } else if (req.path.startsWith('/proxy/8000/media')) {
    req.url = req.url.replace('/proxy/8000', '');
    return express.static(path.join(__dirname, 'media'))(req, res, next);
  }
  next();
});

// Proxy all other requests to Django
app.all('*', (req, res) => {
  let reqPath = req.originalUrl;
  if (reqPath.startsWith('/proxy/8000')) {
    reqPath = reqPath.replace('/proxy/8000', '');
  }
  
  const options = {
    hostname: '127.0.0.1',
    family: 4,
    port: 8000,
    path: reqPath,
    method: req.method,
    headers: req.headers
  };

  const proxyReq = http.request(options, (proxyRes) => {
    res.writeHead(proxyRes.statusCode, proxyRes.headers);
    proxyRes.pipe(res);
  });

  proxyReq.on('error', (err) => {
    console.error('Proxy error:', err);
    res.status(503).send('Service unavailable');
  });

  if (req.method !== 'GET' && req.method !== 'HEAD') {
    req.pipe(proxyReq);
  } else {
    proxyReq.end();
  }
});

const PORT = process.env.PORT || 443;
app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server running on port ${PORT}`);
});
