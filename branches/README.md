# Branches App

This Django app provides comprehensive branch management functionality for the BranchPoint backend, including branch CRUD operations, manager assignment, and branch-scoped access control.

## Features

- Complete branch management (SuperAdmin only)
- Manager assignment and reassignment
- Branch-scoped access control
- Branch statistics and reporting
- Staff management per branch
- Search and filtering capabilities

## Models

### Branch
- `name`: Branch name (unique)
- `location`: Branch location
- `description`: Branch description
- `is_active`: Branch status
- `manager`: One-to-one relationship with User (manager role)
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

## API Endpoints

### Branch Management (SuperAdmin Only)
- `GET /api/branches/` - List all branches
- `POST /api/branches/` - Create new branch
- `GET /api/branches/{id}/` - Get specific branch
- `PUT /api/branches/{id}/` - Update specific branch
- `DELETE /api/branches/{id}/` - Delete specific branch

### Current User's Branch (Manager/Staff)
- `GET /api/branches/my-branch/` - Get current user's assigned branch

### Branch Statistics
- `GET /api/branches/{id}/stats/` - Get branch statistics
- `GET /api/branches/my-branch/stats/` - Get current user's branch statistics

### Branch Staff Management
- `GET /api/branches/{id}/staff/` - Get staff list for branch
- `GET /api/branches/my-branch/staff/` - Get current user's branch staff

### Manager Assignment (SuperAdmin Only)
- `POST /api/branches/{id}/assign-manager/` - Assign manager to branch
- `POST /api/branches/{id}/remove-manager/` - Remove manager from branch
- `GET /api/branches/available-managers/` - Get available managers

### Bulk Operations (SuperAdmin Only)
- `POST /api/branches/{id}/bulk-assign-staff/` - Bulk assign staff to branch

### Search and Utilities
- `GET /api/branches/search/?q=query` - Search branches
- `GET /api/branches/global-stats/` - Get global branch statistics

## Request/Response Examples

### Create Branch
```json
POST /api/branches/
{
    "name": "Main Branch",
    "location": "Nairobi, Kenya",
    "description": "Main headquarters branch",
    "is_active": true,
    "manager_id": 1
}
```

### Assign Manager
```json
POST /api/branches/1/assign-manager/
{
    "manager_id": 2
}
```

### Bulk Assign Staff
```json
POST /api/branches/1/bulk-assign-staff/
{
    "staff_ids": [3, 4, 5]
}
```

### Search Branches
```
GET /api/branches/search/?q=nairobi
```

## Permissions

### Role-Based Access Control
- **SuperAdmin**: Full access to all branches and operations
- **Manager**: Access only to their assigned branch
- **Staff**: Access only to their assigned branch (read-only)

### Custom Permission Classes
- `IsSuperAdmin`: Only super admins
- `IsManager`: Only managers
- `IsManagerOrSuperAdmin`: Managers or super admins
- `IsBranchManager`: Branch managers for their branch
- `IsBranchStaff`: Staff for their assigned branch
- `CanAccessBranch`: Check if user can access a specific branch
- `CanManageBranch`: Check if user can manage a specific branch

## Branch-Scoped Logic

### Visibility Rules
- **SuperAdmin**: Can view and manage all branches
- **Manager**: Can only view and manage their assigned branch
- **Staff**: Can only view their assigned branch

### CRUD Operations
- All staff, vendor, product, and sale operations are scoped to the user's branch
- Users must be assigned to a branch before they can operate on resources
- Branch assignment is enforced at the model level

## Statistics and Reporting

### Branch Statistics
- Staff count
- Total products
- Total vendors
- Total sales
- Total revenue

### Global Statistics (SuperAdmin Only)
- Total branches
- Active branches
- Branches with managers
- Total staff
- Total managers

## Management Commands

### Create Branch
```bash
python manage.py createbranch --name "Main Branch" --location "Nairobi" --description "HQ" --manager-email "manager@example.com"
```

## Signals

- Automatic validation of manager assignments
- Prevention of branch deletion with associated data
- Automatic user-branch relationship management

## Dependencies

- Django REST Framework
- Custom User model from accounts app
- Role-based permissions system 