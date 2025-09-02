const express = require('express');
const cors = require('cors');
const path = require('path');

const app = express();
const PORT = 8002;

// Enable CORS for all routes
app.use(cors());

// Serve static files from public directory
app.use(express.static(path.join(__dirname, 'public')));

// Serve the main HTML file for all routes (SPA routing)
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.listen(PORT, () => {
  console.log(`PKCE OAuth2 SPA server running at http://localhost:${PORT}`);
  console.log('This SPA will communicate with the OAuth2 server at http://localhost:8000');
});
