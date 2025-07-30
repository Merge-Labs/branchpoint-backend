# Sales Accounts App

This Django app provides comprehensive sales account management functionality that matches your frontend requirements.

## Features

### Sales Account Management
- **Company Information**: Name, contact person, email, phone, location
- **Account Details**: Account value, status tracking, deals count
- **Status Management**: Prospect, Active, Negotiation, Closed
- **Assignment**: Assign accounts to specific users
- **Activity Tracking**: Track all contact activities and interactions

### Deal Management
- **Deal Stages**: Prospecting, Qualification, Proposal, Negotiation, Closed Won/Lost
- **Deal Value**: Track monetary value of each deal
- **Probability**: Set win probability percentage
- **Timeline**: Expected close dates and tracking

### Contact Activity Tracking
- **Activity Types**: Phone calls, emails, meetings, notes, proposals
- **Activity History**: Complete audit trail of all interactions
- **Deal Association**: Link activities to specific deals
- **Automatic Updates**: Last contact date updates automatically

## API Endpoints

### Sales Accounts

#### List/Create Accounts
```
GET /api/salesaccounts/accounts/
POST /api/salesaccounts/accounts/
```

**Query Parameters:**
- `search`: Search by company name, contact person, or email
- `status`: Filter by status (all, prospect, active, negotiation, closed)

**POST Data:**
```json
{
  "name": "TechCorp Solutions",
  "contact_person": "Sarah Johnson",
  "email": "sarah.johnson@techcorp.com",
  "phone": "+1 (555) 123-4567",
  "location": "San Francisco, CA",
  "account_value": 125000.00,
  "status": "active",
  "assigned_to": 1
}
```

#### Account Details
```
GET /api/salesaccounts/accounts/{id}/
PUT /api/salesaccounts/accounts/{id}/
DELETE /api/salesaccounts/accounts/{id}/
```

#### Update Account Status
```
POST /api/salesaccounts/accounts/{id}/status/
```
**Data:** `{"status": "active"}`

#### Assign Account
```
POST /api/salesaccounts/accounts/{id}/assign/
```
**Data:** `{"user_id": 1}`

### Deals

#### List/Create Deals for Account
```
GET /api/salesaccounts/accounts/{account_id}/deals/
POST /api/salesaccounts/accounts/{account_id}/deals/
```

**POST Data:**
```json
{
  "title": "Enterprise Software License",
  "value": 50000.00,
  "stage": "negotiation",
  "expected_close_date": "2024-02-15",
  "probability": 75
}
```

### Contact Activities

#### List/Create Activities for Account
```
GET /api/salesaccounts/accounts/{account_id}/activities/
POST /api/salesaccounts/accounts/{account_id}/activities/
```

**POST Data:**
```json
{
  "activity_type": "meeting",
  "subject": "Product Demo",
  "description": "Demonstrated new features to the team",
  "deal": 1
}
```

### Statistics

#### Get Sales Account Statistics
```
GET /api/salesaccounts/stats/
```

**Response:**
```json
{
  "total_accounts": 4,
  "active_deals": 2,
  "total_value": 459000.00,
  "conversion_rate": 50.0
}
```

## Models

### SalesAccount
- **name**: Company name
- **contact_person**: Primary contact
- **email**: Contact email
- **phone**: Contact phone
- **location**: Company location
- **account_value**: Total account value
- **status**: Current status (prospect/active/negotiation/closed)
- **deals_count**: Number of active deals
- **last_contact_date**: Date of last contact
- **created_by**: User who created the account
- **assigned_to**: User assigned to the account

### Deal
- **account**: Associated sales account
- **title**: Deal description
- **value**: Deal monetary value
- **stage**: Current stage in sales process
- **expected_close_date**: Expected closing date
- **probability**: Win probability percentage
- **created_by**: User who created the deal

### ContactActivity
- **account**: Associated sales account
- **activity_type**: Type of activity (call/email/meeting/note/proposal)
- **subject**: Activity subject
- **description**: Activity details
- **deal**: Associated deal (optional)
- **performed_by**: User who performed the activity
- **activity_date**: When the activity occurred

## Frontend Integration

This backend perfectly matches your frontend requirements:

1. **Account Cards**: All fields needed for account display
2. **Search & Filter**: API supports search and status filtering
3. **Statistics**: Dashboard stats endpoint
4. **Modal Forms**: CRUD operations for accounts
5. **Status Management**: Update account status
6. **Activity Tracking**: Log all interactions

## Usage Examples

### Creating a New Account
```javascript
const newAccount = {
  name: "TechCorp Solutions",
  contact_person: "Sarah Johnson",
  email: "sarah.johnson@techcorp.com",
  phone: "+1 (555) 123-4567",
  location: "San Francisco, CA",
  account_value: 125000,
  status: "active"
};

fetch('/api/salesaccounts/accounts/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify(newAccount)
});
```

### Getting Accounts with Search
```javascript
fetch('/api/salesaccounts/accounts/?search=tech&status=active', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
```

### Getting Statistics
```javascript
fetch('/api/salesaccounts/stats/', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
```

## Admin Interface

The app includes a comprehensive Django admin interface for:
- Managing sales accounts
- Viewing and editing deals
- Tracking contact activities
- User assignment management

Access via `/admin/` and look for the "Sales Accounts" section. 