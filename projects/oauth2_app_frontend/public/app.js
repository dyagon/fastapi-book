// PKCE OAuth2 SPA Application using Vue 3
const { createApp } = Vue;

// OAuth2 Configuration
const OAUTH_CONFIG = {
    clientId: 'pkce-public-client',
    redirectUri: 'http://localhost:8002/callback',
    authServerUrl: 'http://localhost:8000',
    resourceServerUrl: 'http://localhost:8000/api',
    scopes: ['get_user_info', 'get_admin_info', 'get_client_info']
};

// Utility Functions for PKCE
const PKCEUtils = {
    // Generate random string for code_verifier
    generateCodeVerifier() {
        const array = new Uint8Array(32);
        crypto.getRandomValues(array);
        return this.base64URLEncode(array);
    },

    // Generate code_challenge from code_verifier using SHA256
    async generateCodeChallenge(codeVerifier) {
        const encoder = new TextEncoder();
        const data = encoder.encode(codeVerifier);
        const digest = await crypto.subtle.digest('SHA-256', data);
        return this.base64URLEncode(new Uint8Array(digest));
    },

    // Base64 URL encoding (without padding)
    base64URLEncode(buffer) {
        return btoa(String.fromCharCode(...buffer))
            .replace(/\+/g, '-')
            .replace(/\//g, '_')
            .replace(/=/g, '');
    },

    // Generate random state parameter
    generateState() {
        const array = new Uint8Array(16);
        crypto.getRandomValues(array);
        return this.base64URLEncode(array);
    }
};

// Main Vue Application
createApp({
    data() {
        return {
            // UI State
            currentStep: 1,
            isLoading: false,
            
            // Step completion tracking
            step1Completed: false,
            step2Completed: false,
            step3Completed: false,
            step4Completed: false,
            
            // PKCE Parameters
            pkceParams: {
                codeVerifier: null,
                codeChallenge: null,
                state: null
            },
            
            // OAuth Flow Data
            authorizationUrl: null,
            authorizationCode: null,
            tokenResponse: null,
            tokenError: null,
            
            // API Testing
            apiResponse: null,
            apiError: null,
            
            // Configuration
            requestedScopes: OAUTH_CONFIG.scopes
        };
    },

    mounted() {
        // Check if we're coming back from authorization (callback)
        this.handleCallback();
    },

    methods: {
        // Step 1: Generate PKCE parameters
        async generatePKCE() {
            this.isLoading = true;
            try {
                const codeVerifier = PKCEUtils.generateCodeVerifier();
                const codeChallenge = await PKCEUtils.generateCodeChallenge(codeVerifier);
                const state = PKCEUtils.generateState();

                this.pkceParams = {
                    codeVerifier,
                    codeChallenge,
                    state
                };

                this.step1Completed = true;
                this.currentStep = 2;
                
                console.log('PKCE parameters generated:', this.pkceParams);
            } catch (error) {
                console.error('Error generating PKCE parameters:', error);
                alert('生成 PKCE 参数时出错：' + error.message);
            } finally {
                this.isLoading = false;
            }
        },

        // Step 2: Start authorization flow
        startAuthorization() {
            if (!this.step1Completed) {
                alert('请先生成 PKCE 参数');
                return;
            }

            // Build authorization URL
            const params = new URLSearchParams({
                response_type: 'code',
                client_id: OAUTH_CONFIG.clientId,
                redirect_uri: OAUTH_CONFIG.redirectUri,
                scope: OAUTH_CONFIG.scopes.join(' '),
                state: this.pkceParams.state,
                code_challenge: this.pkceParams.codeChallenge,
                code_challenge_method: 'S256'
            });

            this.authorizationUrl = `${OAUTH_CONFIG.authServerUrl}/oauth2/authorize?${params.toString()}`;
            
            console.log('Authorization URL:', this.authorizationUrl);
            
            // Store PKCE parameters in sessionStorage for when we come back
            sessionStorage.setItem('pkceParams', JSON.stringify(this.pkceParams));
            sessionStorage.setItem('oauthState', 'authorization_started');
            
            // Redirect to authorization server
            window.location.href = this.authorizationUrl;
        },

        // Handle callback from authorization server
        handleCallback() {
            const urlParams = new URLSearchParams(window.location.search);
            const code = urlParams.get('code');
            const state = urlParams.get('state');
            const error = urlParams.get('error');

            if (error) {
                this.tokenError = `授权失败: ${error} - ${urlParams.get('error_description') || ''}`;
                return;
            }

            if (code && state) {
                // Restore PKCE parameters from sessionStorage
                const storedParams = sessionStorage.getItem('pkceParams');
                const oauthState = sessionStorage.getItem('oauthState');
                
                if (storedParams && oauthState === 'authorization_started') {
                    this.pkceParams = JSON.parse(storedParams);
                    this.step1Completed = true;
                    
                    // Verify state parameter
                    if (state !== this.pkceParams.state) {
                        this.tokenError = 'State 参数不匹配，可能存在 CSRF 攻击';
                        return;
                    }
                    
                    this.authorizationCode = code;
                    this.step2Completed = true;
                    this.currentStep = 3;
                    
                    // Clean up URL
                    window.history.replaceState({}, document.title, window.location.pathname);
                    
                    // Clean up sessionStorage
                    sessionStorage.removeItem('pkceParams');
                    sessionStorage.removeItem('oauthState');
                    
                    console.log('Authorization code received:', code);
                }
            }
        },

        // Step 3: Exchange authorization code for tokens
        async exchangeToken() {
            if (!this.step2Completed || !this.authorizationCode) {
                alert('请先完成授权流程');
                return;
            }

            this.isLoading = true;
            this.tokenError = null;

            try {
                const tokenData = new URLSearchParams({
                    grant_type: 'authorization_code',
                    code: this.authorizationCode,
                    redirect_uri: OAUTH_CONFIG.redirectUri,
                    client_id: OAUTH_CONFIG.clientId,
                    code_verifier: this.pkceParams.codeVerifier
                });

                const response = await fetch(`${OAUTH_CONFIG.authServerUrl}/oauth2/token`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: tokenData.toString()
                });

                if (response.ok) {
                    this.tokenResponse = await response.json();
                    this.step3Completed = true;
                    this.currentStep = 4;
                    
                    console.log('Token response:', this.tokenResponse);
                } else {
                    const errorData = await response.json();
                    this.tokenError = `${response.status}: ${errorData.detail || response.statusText}`;
                }
            } catch (error) {
                console.error('Token exchange error:', error);
                this.tokenError = `网络错误: ${error.message}`;
            } finally {
                this.isLoading = false;
            }
        },

        // Step 4: Test API endpoints
        async callAPI(endpoint, description) {
            if (!this.step3Completed || !this.tokenResponse) {
                alert('请先获取访问令牌');
                return;
            }

            this.apiError = null;

            try {
                const response = await fetch(`${OAUTH_CONFIG.resourceServerUrl}${endpoint}`, {
                    method: 'GET',
                    headers: {
                        'Authorization': `Bearer ${this.tokenResponse.access_token}`,
                        'Content-Type': 'application/json'
                    }
                });

                if (response.ok) {
                    const data = await response.json();
                    this.apiResponse = {
                        endpoint: endpoint,
                        description: description,
                        status: response.status,
                        data: data
                    };
                    this.step4Completed = true;
                } else {
                    const errorData = await response.json();
                    this.apiError = `${description} 失败: ${response.status} - ${errorData.detail || response.statusText}`;
                }
            } catch (error) {
                console.error('API call error:', error);
                this.apiError = `${description} 网络错误: ${error.message}`;
            }
        },

        // API test methods
        async testUserInfo() {
            await this.callAPI('/user/info', '获取用户信息');
        },

        async testAdminInfo() {
            await this.callAPI('/admin/info', '获取管理员信息');
        },

        async testUserMe() {
            await this.callAPI('/user/me', '获取当前用户');
        }
    }
}).mount('#app');
