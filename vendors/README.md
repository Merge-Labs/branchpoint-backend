# Vendors App

This Django app provides comprehensive vendor management functionality for the BranchPoint backend, with branch-scoped access control and manager-only permissions for vendor operations.

## Purpose

The vendors app manages supplier relationships at the branch level, ensuring that:
- Vendors are scoped to individual branches
- Only BranchManagers can create/edit vendors in their branch
- Products are associated with vendors (who supplies what)
- Branch-scoped visibility and CRUD operations

## Features

- Complete vendor management (BranchManagers only for creation/editing)
- Branch-scoped access control
- Vendor statistics and reporting
- Product and purchase tracking per vendor
- Search and filtering capabilities
- Bulk operations for vendor management

## Models

### Vendor
- `name`: Vendor name (unique within branch)
- `contact_person`: Primary contact person
- `phone_number`: Contact phone number
- `email`: Contact email address
- `address`: Vendor address
- `description`: Vendor description
- `is_active`: Vendor status
- `vendor_type`: Type of vendor (supplier, service_provider, contractor, other)
- `payment_terms`: Payment terms
- `tax_id`: Tax identification number
- `website`: Vendor website URL
- `branch`: Associated branch (ForeignKey)
- `added_by`: User who added the vendor (ForeignKey)
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

## API Endpoints

### Vendor Management
- `GET /api/vendors/` - List vendors (branch-scoped)
- `POST /api/vendors/` - Create new vendor (BranchManagers only)
- `GET /api/vendors/{id}/` - Get specific vendor
- `PUT /api/vendors/{id}/` - Update specific vendor (BranchManagers only)
- `DELETE /api/vendors/{id}/` - Delete specific vendor (BranchManagers only)

### Vendor Details
- `GET /api/vendors/{id}/stats/` - Get vendor statistics
- `GET /api/vendors/{id}/products/` - Get products supplied by vendor
- `GET /api/vendors/{id}/purchases/` - Get purchases from vendor

### Search and Filtering
- `GET /api/vendors/search/?q=query` - Search vendors by name, contact, or email
- `GET /api/vendors/type/{vendor_type}/` - Get vendors by type
- `GET /api/vendors/active/` - Get only active vendors

### Statistics and Bulk Operations
- `GET /api/vendors/stats/summary/` - Get vendor statistics summary
- `POST /api/vendors/bulk-update-status/` - Bulk update vendor status (BranchManagers only)

## Request/Response Examples

### Create Vendor
```json
POST /api/vendors/
{
    "name": "ABC Supplies",
    "contact_person": "John Doe",
    "phone_number": "+1234567890",
    "email": "john@abcsupplies.com",
    "address": "123 Main St, City, State",
    "description": "Office supplies vendor",
    "vendor_type": "supplier",
    "payment_terms": "Net 30",
    "tax_id": "12-3456789",
    "website": "https://abcsupplies.com"
}
```

### Update Vendor
```json
PUT /api/vendors/1/
{
    "name": "ABC Supplies Ltd",
    "contact_person": "Jane Smith",
    "phone_number": "+1234567891",
    "email": "jane@abcsupplies.com",
    "is_active": true
}
```

### Search Vendors
```
GET /api/vendors/search/?q=ABC
```

### Bulk Update Status
```json
POST /api/vendors/bulk-update-status/
{
    "vendor_ids": [1, 2, 3],
    "is_active": false
}
```

## Permissions

### Role-Based Access Control
- **SuperAdmin**: Full access to all vendors across all branches
- **BranchManager**: Can create, read, update, delete vendors only in their managed branch
- **Staff**: Can only read vendors in their assigned branch

### Custom Permission Classes
- `IsSuperAdmin`: Only super admins
- `IsManager`: Only managers
- `IsManagerOrSuperAdmin`: Managers or super admins
- `IsBranchManager`: Branch managers for their branch
- `CanAccessVendor`: Check if user can access a specific vendor
- `CanManageVendor`: Check if user can manage a specific vendor
- `CanCreateVendor`: Check if user can create vendors

## Branch-Scoped Logic

### Visibility Rules
- **SuperAdmin**: Can view and manage all vendors across all branches
- **BranchManager**: Can only view and manage vendors in their managed branch
- **Staff**: Can only view vendors in their assigned branch

### CRUD Operations
- All vendor operations are scoped to the user's branch
- BranchManagers can only create/edit vendors in their managed branch
- Staff can only view vendors in their assigned branch
- Branch assignment is enforced at the model level

## Statistics and Reporting

### Vendor Statistics
- Total products supplied
- Total purchases made
- Total amount spent
- Last purchase date

### Summary Statistics
- Total vendors per branch
- Active vendors count
- Vendors by type
- Top vendors by spending

## Management Commands

### Create Vendor
```bash
python manage.py createvendor --name "ABC Supplies" --branch "Main Branch" --contact-person "John Doe" --phone "+1234567890" --email "john@abc.com" --vendor-type "supplier"
```

## Signals

- Automatic validation of vendor data
- Prevention of vendor deletion with associated products or purchases
- Automatic branch assignment for new vendors

## Dependencies

- Django REST Framework
- Custom User model from accounts app
- Branch model from branches app
- Role-based permissions system 