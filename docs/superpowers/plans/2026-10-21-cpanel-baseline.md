# Belnu cPanel baseline implementation plan

Goal: reconcile the uploaded cPanel application with GitHub without changing the live site.

Architecture: preserve the cPanel application behavior and migrations 0011–0017 in a review branch. Externalize private configuration and document the server-side preparation before deployment. Keep database, uploads, virtual environments and generated admin assets out of the change.

Constraints: preserve Python 3.7 syntax; do not upgrade Django or change order pricing in this baseline; do not merge or deploy automatically.

- [x] Restore changed application files, templates, custom JavaScript and seven exact migrations from the supplied archive.
- [x] Replace embedded credentials with environment configuration, and provide a preparation script that preserves live values in the private environment file with a backup.
- [x] Verify Python syntax, exact migration contents, private-value exclusion, and configuration preservation using synthetic credentials.
- [ ] Publish a draft pull request with deployment prerequisites and known inherited defects.

Review focus: preserve the active secret key, database credentials, and SMTP credentials; do not run migrations or touch application data; preserve filename case in password templates; keep existing order behavior; disclose that runtime validation on Python 3.7 and MySQL remains pending.
