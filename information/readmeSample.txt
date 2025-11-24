Security Measures Implemented:
- Passwords hashed with bcrypt/argon2.
- Role-based access control.
- Tenant isolation at DB query level.
- Idempotent billing runs prevent duplicate payouts.

Future Security Enhancements:
- Field-level encryption for vendor contact_info and employee phone numbers using pgcrypto.
- Secrets management using environment variables or Vault/KMS.
- Periodic key rotation policy.