const http = require('http');
const https = require('https');
const url = require('url');

const PORT = 3000;

const server = http.createServer((req, res) => {
  // Add CORS headers to every response
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

  // Handle preflight requests
  if (req.method === 'OPTIONS') {
    res.writeHead(204);
    res.end();
    return;
  }

  // Only handle POST requests for our use case
  if (req.method === 'POST') {
    let body = '';
    
    req.on('data', chunk => {
      body += chunk.toString();
    });

    req.on('end', () => {
      // Get the target URL from the query string or default to the one in the user request
      // We expect the client to send the full target URL in a custom header or query param, 
      // OR we can just hardcode the logic to parse the intent.
      // For simplicity in this specific "fix", let's expect the client to send the target URL
      // in a query parameter named 'target', e.g., http://localhost:3000/?target=https://...
      
      const parsedUrl = url.parse(req.url, true);
      const targetUrlStr = parsedUrl.query.target;

      if (!targetUrlStr) {
        res.writeHead(400, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: 'Missing target URL parameter' }));
        return;
      }

      console.log(`Proxying request to: ${targetUrlStr}`);

      try {
        const targetUrl = new URL(targetUrlStr);
        const options = {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            // Forward the Authorization header if present
            ...(req.headers.authorization ? { 'Authorization': req.headers.authorization } : {})
          }
        };

        const proxyReq = https.request(targetUrl, options, (proxyRes) => {
          res.writeHead(proxyRes.statusCode, proxyRes.headers);
          proxyRes.pipe(res);
        });

        proxyReq.on('error', (e) => {
          console.error(`Problem with request: ${e.message}`);
          res.writeHead(502, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ error: `Proxy Error: ${e.message}` }));
        });

        // Write data to request body
        proxyReq.write(body);
        proxyReq.end();

      } catch (error) {
        res.writeHead(400, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: 'Invalid Target URL' }));
      }
    });
  } else {
    res.writeHead(405, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ error: 'Method Not Allowed' }));
  }
});

server.listen(PORT, () => {
  console.log(`Fast Proxy running on port ${PORT}`);
  console.log(`Usage: Send POST to http://localhost:${PORT}/?target=<TARGET_URL>`);
});
