# Core Foundation Layer

This is the Core Foundation layer of the Email Panel System. It provides essential services that all modules depend on.

## IMPORTANT: This layer is STABLE - DO NOT MODIFY without approval

The Core Foundation provides:
- Database access and connection management
- Encryption services for passwords and sensitive data
- Authentication and session management
- Common utilities and logging

## Structure

- `database/` - Database connection and query services
- `encryption/` - Master key management and crypto operations
- `auth/` - Authentication and session management
- `utils/` - Common utilities, logging, and error handling

## Usage

All modules MUST use Core services for:
1. Database access (never connect directly)
2. Encryption/decryption of sensitive data
3. User authentication
4. Logging and error handling

## Interfaces

Core services are accessed through defined interfaces. Never import Core internals directly from modules.