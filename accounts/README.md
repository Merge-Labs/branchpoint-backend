# Accounts App

This Django app provides comprehensive user authentication and management functionality for the BranchPoint backend.

## Features

- Custom User model with role-based access control
- JWT-based authentication
- User registration and login
- Profile management
- Password change functionality
- Role-based permissions
- User statistics and management

## Models

### User
- `email`: Primary identifier (unique)
- `role`: User role (superadmin, manager, staff)
- `branch`: Associated branch (optional)
- `is_active`: Account status
- `date_joined`: Registration date

### Profile
- `user`: One-to-one relationship with User
- `full_name`: User's full name
- `phone`: Phone number (optional)
- `avatar`: Profile picture (optional)

## API Endpoints

### Authentication
- `POST /api/accounts/register/` - Register a new user
- `POST /api/accounts/login/` - Login user
- `POST /api/accounts/logout/` - Logout user
- `GET /api/accounts/me/` - Get current user profile
- `PUT /api/accounts/me/` - Update current user profile

### JWT Tokens
- `POST /api/accounts/token/` - Obtain JWT tokens
- `POST /api/accounts/token/refresh/` - Refresh access token
- `POST /api/accounts/token/verify/` - Verify token

### User Management (Admin Only)
- `GET /api/accounts/users/` - List all users
- `GET /api/accounts/users/{id}/` - Get specific user
- `PUT /api/accounts/users/{id}/` - Update specific user
- `DELETE /api/accounts/users/{id}/` - Delete specific user

### Profile Management
- `PUT /api/accounts/profile/` - Update user profile
- `POST /api/accounts/change-password/` - Change password

### Utility
- `POST /api/accounts/check-email/` - Check email availability
- `GET /api/accounts/stats/` - Get user statistics (admin only)

## Request/Response Examples

### Register User
```json
POST /api/accounts/register/
{
    "email": "user@example.com",
    "password": "securepassword123",
    "password_confirm": "securepassword123",
    "role": "staff",
    "branch": 1,
    "profile": {
        "full_name": "John Doe",
        "phone": "+1234567890"
    }
}
```

### Login
```json
POST /api/accounts/login/
{
    "email": "user@example.com",
    "password": "securepassword123"
}
```

### Update Profile
```json
PUT /api/accounts/profile/
{
    "full_name": "John Smith",
    "phone": "+1234567890"
}
```

## Permissions

### Custom Permission Classes
- `IsSuperAdmin`: Only super admins
- `IsManager`: Only managers
- `IsManagerOrSuperAdmin`: Managers or super admins
- `IsOwnerOrManager`: Object owners or managers
- `IsBranchManager`: Branch managers for their branch

## Management Commands

### Create Superuser
```bash
python manage.py createcustomsuperuser --email admin@example.com --password securepass --full-name "Admin User"
```

## Signals

- Automatically creates a Profile when a User is created
- Automatically saves Profile when User is saved

## Dependencies

- Django REST Framework
- djangorestframework-simplejwt
- django-cors-headers
- Pillow (for image uploads)
- Cloudinary (for file storage) 