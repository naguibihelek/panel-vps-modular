# VPS Management Module - Features

## Feature List

### 1. Server Registration and Management

#### 1.1 Add New Server
- **Description**: Register a new mail VPS server in the system
- **Inputs**: 
  - Server hostname/IP
  - SSH credentials
  - Database connection details
  - Server type (Postfix/Dovecot, etc.)
- **Process**:
  1. Validate server connectivity
  2. Test database connection
  3. Encrypt and store credentials
  4. Set initial status to 'active'
- **Output**: Server ID and confirmation

#### 1.2 List All Servers
- **Description**: Display all registered servers with status
- **Filters**:
  - By status (active/inactive/maintenance)
  - By server type
  - By domain association
- **Display**: Table with hostname, IP, status, domain count, mailbox count

#### 1.3 View Server Details
- **Description**: Show comprehensive server information
- **Includes**:
  - Basic server info
  - Associated domains
  - Connection status
  - Last connectivity check
  - Resource usage (if available)
- **Actions**: Edit, Test Connection, View Logs

#### 1.4 Update Server Configuration
- **Description**: Modify server settings
- **Editable Fields**:
  - SSH credentials
  - Database credentials
  - Server status
  - Server metadata
- **Security**: Requires admin authentication

#### 1.5 Delete Server
- **Description**: Remove server from system
- **Pre-checks**:
  - No active mailboxes
  - No associated domains
  - Confirmation required
- **Process**:
  1. Emit `server.pre_delete` event
  2. Wait for module confirmations
  3. Remove server record
  4. Clean up credentials

### 2. Domain Management

#### 2.1 Add Domain to Server
- **Description**: Associate a domain with a mail server
- **Inputs**:
  - Domain name
  - Server selection
  - MX record priority
- **Validation**:
  - Domain format validation
  - Duplicate check
  - Server capacity check
- **Auto-configuration**: Generate recommended DNS records

#### 2.2 List Domains
- **Description**: Display all domains across all servers
- **Views**:
  - By server grouping
  - By verification status
  - By creation date
- **Quick Actions**: Verify, Edit DNS, Remove

#### 2.3 Domain Verification
- **Description**: Verify domain ownership and configuration
- **Checks**:
  - MX record pointing to server
  - SPF record present
  - DKIM configured
  - DMARC policy set
- **Status Updates**: Real-time verification status

#### 2.4 DNS Record Management
- **Description**: Configure and display required DNS records
- **Record Types**:
  - MX records with priority
  - SPF TXT record
  - DKIM TXT record
  - DMARC TXT record
- **Features**:
  - Copy-to-clipboard functionality
  - Validation checking
  - Example records provided

#### 2.5 Remove Domain
- **Description**: Disassociate domain from server
- **Pre-checks**:
  - No active mailboxes using domain
  - Confirmation required
- **Cleanup**: Remove all associated DNS records

### 3. Connection Management

#### 3.1 Test Server Connection
- **Description**: Verify server is accessible
- **Tests**:
  - SSH connectivity
  - Database connection
  - Mail service status
- **Results**: Detailed test report with timing

#### 3.2 Credential Rotation
- **Description**: Update server access credentials
- **Process**:
  1. Validate new credentials
  2. Test with new credentials
  3. Encrypt and store
  4. Invalidate old credentials
- **Rollback**: Automatic on failure

#### 3.3 Connection Pool Management
- **Description**: Manage database connection pools
- **Features**:
  - Pool size configuration
  - Connection timeout settings
  - Automatic reconnection
  - Connection statistics

### 4. Server Monitoring

#### 4.1 Status Dashboard
- **Description**: Overview of all server statuses
- **Displays**:
  - Server up/down status
  - Last check timestamp
  - Response times
  - Error counts
- **Refresh**: Auto-refresh every 5 minutes

#### 4.2 Connectivity Alerts
- **Description**: Alert on server issues
- **Triggers**:
  - Connection failure
  - Slow response time
  - Database unavailable
- **Actions**: Email notification, log entry

#### 4.3 Bulk Status Check
- **Description**: Check all servers simultaneously
- **Process**: Parallel connectivity tests
- **Report**: Summary of all server statuses

### 5. Security Features

#### 5.1 Credential Encryption
- **Description**: Secure storage of all passwords
- **Method**: AES-256 encryption via Core
- **Access**: Only through secure interfaces

#### 5.2 Access Logging
- **Description**: Track all credential access
- **Logs**:
  - Who accessed
  - When accessed
  - What operation
  - Success/failure
- **Retention**: 90 days

#### 5.3 SSH Key Management
- **Description**: Use SSH keys instead of passwords
- **Features**:
  - Generate key pairs
  - Deploy public keys
  - Rotate keys periodically
- **Security**: Private keys encrypted

### 6. Administrative Tools

#### 6.1 Bulk Server Import
- **Description**: Import multiple servers from CSV
- **Format**: hostname,ip,ssh_user,ssh_pass,db_host,db_user,db_pass
- **Validation**: Test each server before import
- **Report**: Success/failure per server

#### 6.2 Server Export
- **Description**: Export server configurations
- **Format**: CSV or JSON
- **Excludes**: Passwords (security)
- **Use Case**: Backup, documentation

#### 6.3 Maintenance Mode
- **Description**: Mark server for maintenance
- **Effects**:
  - Prevents new mailbox creation
  - Displays warning in UI
  - Skips in automated processes
- **Notification**: Alert affected users

---

**Version**: 1.0.0  
**Status**: Final  
**Last Updated**: July 2024