import pytest
import json


class TestAuthEndpoints:
    """Test cases for authentication endpoints."""
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get('/api/health')
        assert response.status_code == 200
        data = response.json
        assert data['status'] == 'healthy'
        assert 'message' in data
    
    def test_user_registration(self, client):
        """Test user registration."""
        user_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'SecurePass123'
        }
        
        response = client.post('/api/auth/register', json=user_data)
        assert response.status_code == 201
        
        data = response.json
        assert data['message'] == 'User registered successfully'
        assert 'access_token' in data
        assert 'refresh_token' in data
        assert data['user']['username'] == user_data['username']
        assert data['user']['email'] == user_data['email']
    
    def test_duplicate_username(self, client):
        """Test registration with duplicate username."""
        user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'SecurePass123'
        }
        
        # First registration
        client.post('/api/auth/register', json=user_data)
        
        # Duplicate registration
        response = client.post('/api/auth/register', json=user_data)
        assert response.status_code == 409
        assert 'Username already exists' in response.json['error']
    
    def test_invalid_email(self, client):
        """Test registration with invalid email."""
        user_data = {
            'username': 'testuser2',
            'email': 'invalid-email',
            'password': 'SecurePass123'
        }
        
        response = client.post('/api/auth/register', json=user_data)
        assert response.status_code == 400
        assert 'Invalid email format' in response.json['error']
    
    def test_weak_password(self, client):
        """Test registration with weak password."""
        user_data = {
            'username': 'testuser3',
            'email': 'test3@example.com',
            'password': 'weak'
        }
        
        response = client.post('/api/auth/register', json=user_data)
        assert response.status_code == 400
        assert 'Password must be at least 8 characters' in response.json['error']
    
    def test_user_login(self, client):
        """Test user login."""
        # Register user first
        reg_data = {
            'username': 'logintest',
            'email': 'login@example.com',
            'password': 'SecurePass123'
        }
        client.post('/api/auth/register', json=reg_data)
        
        # Test login with username
        login_data = {
            'login': 'logintest',
            'password': 'SecurePass123'
        }
        response = client.post('/api/auth/login', json=login_data)
        assert response.status_code == 200
        
        data = response.json
        assert data['message'] == 'Login successful'
        assert 'access_token' in data
        assert 'refresh_token' in data
        assert data['user']['username'] == reg_data['username']
    
    def test_login_with_email(self, client):
        """Test login with email."""
        # Register user first
        reg_data = {
            'username': 'emaillogin',
            'email': 'emaillogin@example.com',
            'password': 'SecurePass123'
        }
        client.post('/api/auth/register', json=reg_data)
        
        # Test login with email
        login_data = {
            'login': 'emaillogin@example.com',
            'password': 'SecurePass123'
        }
        response = client.post('/api/auth/login', json=login_data)
        assert response.status_code == 200
    
    def test_invalid_credentials(self, client):
        """Test login with invalid credentials."""
        login_data = {
            'login': 'nonexistent',
            'password': 'WrongPassword'
        }
        response = client.post('/api/auth/login', json=login_data)
        assert response.status_code == 401
        assert 'Invalid credentials' in response.json['error']
    
    def test_get_profile(self, client, auth_headers):
        """Test getting user profile."""
        response = client.get('/api/auth/profile', headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json
        assert 'user' in data
        assert data['user']['username'] == 'testuser'
        assert data['user']['email'] == 'test@example.com'
    
    def test_profile_without_auth(self, client):
        """Test accessing profile without authentication."""
        response = client.get('/api/auth/profile')
        assert response.status_code == 401
        assert 'Authorization required' in response.json['error']
    
    def test_update_profile(self, client, auth_headers):
        """Test updating user profile."""
        update_data = {
            'timezone': 'Europe/London',
            'skill_level': 'advanced',
            'preferences': {
                'daily_reminder_time': '10:00',
                'email_notifications': False
            }
        }
        
        response = client.put('/api/auth/profile', 
                            headers=auth_headers, 
                            json=update_data)
        assert response.status_code == 200
        
        data = response.json
        assert data['message'] == 'Profile updated successfully'
        assert data['user']['timezone'] == 'Europe/London'
        assert data['user']['skill_level'] == 'advanced'
        assert data['user']['preferences']['daily_reminder_time'] == '10:00'
    
    def test_change_password(self, client, auth_headers):
        """Test changing password."""
        password_data = {
            'old_password': 'TestPass123',
            'new_password': 'NewSecurePass456'
        }
        
        response = client.post('/api/auth/change-password',
                             headers=auth_headers,
                             json=password_data)
        assert response.status_code == 200
        assert response.json['message'] == 'Password changed successfully'
        
        # Test login with new password
        login_data = {
            'login': 'testuser',
            'password': 'NewSecurePass456'
        }
        response = client.post('/api/auth/login', json=login_data)
        assert response.status_code == 200
    
    def test_change_password_wrong_old(self, client, auth_headers):
        """Test changing password with wrong old password."""
        password_data = {
            'old_password': 'WrongPassword',
            'new_password': 'NewSecurePass456'
        }
        
        response = client.post('/api/auth/change-password',
                             headers=auth_headers,
                             json=password_data)
        assert response.status_code == 401
        assert 'Current password is incorrect' in response.json['error']
    
    def test_token_refresh(self, client):
        """Test token refresh."""
        # Register and get refresh token
        reg_data = {
            'username': 'refreshtest',
            'email': 'refresh@example.com',
            'password': 'SecurePass123'
        }
        response = client.post('/api/auth/register', json=reg_data)
        refresh_token = response.json['refresh_token']
        
        # Refresh token
        headers = {'Authorization': f'Bearer {refresh_token}'}
        response = client.post('/api/auth/refresh', headers=headers)
        assert response.status_code == 200
        
        data = response.json
        assert 'access_token' in data
        assert 'user' in data