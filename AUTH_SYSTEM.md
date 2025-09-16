# MyCrypto Authentication System - Clean Architecture

## Overview

The authentication system has been completely refactored to follow Clean Architecture principles with enhanced security features, proper password validation, and JWT token management.

## Architecture

### Domain Layer
- **AuthUser Entity**: Rich domain entity with authentication-specific behavior
- **Password Value Object**: Secure password handling with bcrypt hashing and validation
- **Email/UserId Value Objects**: Type-safe identifiers with validation

### Application Layer
- **AuthUseCases**: Business logic for authentication operations
- **AuthRepository Interface**: Abstract repository contract
- **DTOs**: Clean data transfer objects for requests/responses

### Infrastructure Layer
- **MongoAuthRepository**: MongoDB implementation of auth repository
- **JWTService**: JWT token creation and verification service

### Presentation Layer
- **Auth Routes**: FastAPI endpoints with proper error handling
- **Auth Schemas**: Pydantic models for API serialization

## Features Implemented

### ✅ User Registration
- Email validation and uniqueness check
- Strong password requirements:
  - Minimum 8 characters
  - At least one uppercase letter
  - At least one lowercase letter
  - At least one digit
  - At least one special character
- Secure bcrypt password hashing
- User creation with verification status

### ✅ User Authentication
- Email/password login
- Account lockout after 5 failed attempts (30 minutes)
- Failed login attempt tracking
- Successful login tracking with timestamp

### ✅ JWT Token Management
- Access tokens (30 minutes expiry)
- Refresh tokens (7 days expiry)
- Token type validation
- Secure token verification

### ✅ Profile Management
- Get user profile
- Update profile information
- Change password with current password verification

### ✅ Security Features
- Account verification system
- Manual account unlock (admin)
- Password strength validation
- Secure password hashing with bcrypt
- JWT token expiration handling

## API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - User login
- `POST /auth/refresh` - Refresh access token
- `POST /auth/logout` - User logout

### Profile Management
- `GET /auth/profile` - Get user profile
- `PUT /auth/profile` - Update profile
- `PUT /auth/change-password` - Change password

### Admin Operations
- `POST /auth/verify/{user_id}` - Verify user account
- `POST /auth/unlock/{user_id}` - Unlock user account

### Token Verification
- `GET /auth/verify` - Verify token validity

## Security Considerations

### Password Security
- **bcrypt hashing**: Industry-standard password hashing
- **Salt rounds**: Automatic salt generation for each password
- **Strength validation**: Comprehensive password requirements
- **No plain text storage**: Passwords are never stored in plain text

### Token Security
- **Short-lived access tokens**: 30-minute expiry reduces exposure
- **Refresh token rotation**: New refresh tokens on each refresh
- **Token type validation**: Prevents token type confusion attacks
- **Secure secret key**: Configurable JWT secret key

### Account Security
- **Account lockout**: Prevents brute force attacks
- **Failed attempt tracking**: Monitors suspicious activity
- **Email uniqueness**: Prevents duplicate accounts
- **Account verification**: Optional email verification workflow

## Configuration

### Environment Variables
```bash
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
```

### Database Schema
The system uses MongoDB with the following user document structure:
```json
{
  "_id": "ObjectId",
  "email": "user@example.com",
  "name": "User Name",
  "password_hash": "bcrypt_hash",
  "created_at": "ISODate",
  "updated_at": "ISODate",
  "is_verified": false,
  "last_login": "ISODate",
  "failed_login_attempts": 0,
  "locked_until": "ISODate"
}
```

## Testing

Use the provided test file `tests/auth-clean.http` for comprehensive testing:

1. **Registration Flow**: Test user registration with validation
2. **Authentication Flow**: Test login and token generation
3. **Profile Management**: Test profile updates and password changes
4. **Token Management**: Test token refresh and verification
5. **Security Testing**: Test weak passwords and duplicate emails
6. **Admin Operations**: Test account verification and unlocking

## Error Handling

The system provides comprehensive error handling:

- **400 Bad Request**: Validation errors, weak passwords, duplicate emails
- **401 Unauthorized**: Invalid credentials, expired tokens, locked accounts
- **404 Not Found**: User not found for admin operations
- **500 Internal Server Error**: Unexpected server errors

## Migration from Legacy Auth

The new authentication system is fully backward compatible and can run alongside the existing auth system. Key improvements:

1. **Enhanced Security**: Stronger password requirements and bcrypt hashing
2. **Better Architecture**: Clean separation of concerns
3. **Improved Validation**: Comprehensive input validation
4. **Account Protection**: Lockout mechanisms and attempt tracking
5. **Token Management**: Proper JWT handling with refresh tokens

## Next Steps

1. **Email Verification**: Implement email verification workflow
2. **Password Reset**: Add password reset functionality
3. **Two-Factor Authentication**: Add 2FA support
4. **Session Management**: Implement token blacklisting
5. **Audit Logging**: Add comprehensive audit trails
