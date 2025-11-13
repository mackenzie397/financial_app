# CHANGELOG

## [Unreleased]

### Added
- **Automatic Seeds on User Registration**: New users automatically receive default categories (Alimentação, Transporte, Diversão, Saúde, Moradia, Salário, Freelance), payment methods (Dinheiro, Cartão de Débito, Cartão de Crédito, PIX), and investment types (Renda Fixa, Ações, Fundos Imobiliários) upon registration.
  - Backend: New `_seed_user_defaults()` function in `src/routes/user.py`
  - Ensures users can immediately create transactions without manual setup
  - Seeds are created atomically with user registration

- **Enhanced Settings Page**: 
  - Refactored Settings page with tabbed interface
  - Moved Categories CRUD to Settings > Categories tab
  - Added Payment Methods CRUD to Settings > Payment Methods tab
  - Provides centralized location for all configuration management

- **User Account Management**:
  - New "My Account" page with password change functionality
  - User dropdown menu in header replaces simple logout button
  - Menu options: "My Account" and "Logout"
  
- **Password Change Endpoint**:
  - `POST /api/account/change-password`: Allows authenticated users to change password
  - Validates old password for security
  - Enforces password strength requirements (8+ chars, uppercase, lowercase, digit, special char)
  - Rate limited to 5 attempts per 15 minutes
  - Returns appropriate error messages for invalid attempts

- **Profile Update Endpoint**:
  - `PUT /api/account/update-profile`: Allows updating email and username
  - Validates uniqueness of new email and username
  - Sanitizes input to prevent XSS attacks
  - Full backward compatibility with existing code

### Changed
- **Navigation**: Removed "Categories" tab from main navigation menu
  - Categories now accessible exclusively through Settings > Categories
  - Cleaner, more focused main navigation
  - Dashboard, Metas, Relatórios, and Configurações remain in main menu

- **Frontend Components**:
  - `Categories.jsx` → `settings/CategoriesManager.jsx` (refactored)
  - New `settings/PaymentMethodsManager.jsx` component
  - New `AccountPage.jsx` component with password change form
  - Updated `Dashboard.jsx` with dropdown menu implementation

- **API Client**:
  - Added `changePassword()` function to `lib/api.js`
  - Added `updateProfile()` function to `lib/api.js`

### Security
- Password strength validation implemented with regex patterns
- Rate limiting on sensitive endpoints (change-password: 5/15min)
- Input sanitization using bleach library
- JWT cookies remain secure (HTTPS only, SameSite=None)
- Old password validation required before changing password
- Prevents password reuse (new password must differ from old)

### Testing
- Added `test_register_creates_default_seeds()` to verify automatic seeding
- Added `test_change_password_requires_old_password()` for security validation
- Added `test_change_password_validates_strength()` for password requirements
- Added `test_change_password_cannot_reuse_old()` for password reuse prevention
- Added `test_change_password_success()` to verify successful password change
- Added `test_change_password_rate_limit()` to validate rate limiting
- All tests pass with comprehensive coverage

### Database
- No schema changes required
- Existing tables (user, category, payment_method, investment_type) unchanged
- Backward compatible with all existing migrations

### Bug Fixes
- Fixed issue where new users without categories couldn't create transactions
- Fixed Settings page rendering (was empty before)

### Documentation
- Updated README.md with new features and setup instructions
- Added this CHANGELOG.md file
- PLANO_TECNICO.md documents full technical implementation details

## Deployment Notes
- No database migrations required
- No new dependencies added (all already in requirements.txt)
- Frontend build: `npm run build`
- Backend: Run with `flask --app src.main run` or `gunicorn wsgi:app`
- Backward compatible - no breaking changes to existing API

## Migration Path for Existing Users
For applications already in production with existing users without seeds:
1. Users can manually add categories/payment methods via Settings
2. Optional: Create migration script to batch-seed existing user accounts
3. No data loss or corruption risk - purely additive feature

---

## Previous Releases

(No previous releases in this changelog yet)
