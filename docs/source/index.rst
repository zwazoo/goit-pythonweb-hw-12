Contacts API
============

A RESTful API for managing personal contacts, built with FastAPI and PostgreSQL.

Features
--------

- User registration and JWT authentication (access & refresh tokens)
- Email verification and password reset via email
- Role-based access control (admin / user)
- CRUD operations for contacts with birthday search
- Avatar upload via Cloudinary
- Redis caching for current user lookups
- Rate limiting with SlowAPI

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   modules
