
# OAuth2 Demo

setup:

```bash
# run oauth and resource at 8000
uv run uvicorn projects.oauth2_server.auth.main:app --reload
```

#### OAuth2 Client Credentials Flow

```bash
# run backend at 8001
uv run uvicorn projects.oauth2_app_backend.main:app --port 8001 --reload
```

in backend:
- get token by client_id and client_secret
- use token to get resource 

test:
```bash
curl http://127.0.0.1:8001/test-client-credentials
# {"client_id":"client-credentials-client","scopes":["get_admin_info","get_user_info","get_client_info"]}
```

### OAuth2 Authorization Code Flow

- open: http://localhost:8001
- click "Login with OAuth2" button, it will redirect to auth server login page
- alice:wonderland
- after login, it will redirect back to client with code
- client will exchange code for access token


### OAuth2 Authorization Code Flow with PKCE

```bash
cd projects/oauth2_app_frontend
npm install # if you haven't installed dependencies yet
npm run dev
```

- open: http://localhost:8002
- follow the steps