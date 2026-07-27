---
name: api-auth-testing
description: Design and implement authentication and authorization test matrices for public, authenticated, and role-protected API endpoints.
compatibility: opencode
metadata:
    domain: api-testing
    phase: authentication
---

# API Authentication and Authorization Testing

Use this skill when integration testing APIs with authentication or authorization boundaries.

The objective is to prove that API access controls work in both positive and negative cases.

# Do not invent authentication

Determine the authentication mechanism from specifications and implementation.

Possible mechanisms include:

* Bearer tokens
* JWT
* OAuth2
* OpenID Connect
* API keys
* session cookies
* Basic authentication
* custom authentication headers
* test-only authentication helpers

Use the mechanism actually supported by the application.

# Credential acquisition

Prefer test credentials in this order:

1. existing test fixture or helper
2. documented authentication endpoint
3. seeded test identity
4. environment-provided test credentials

Never hard-code production credentials or real secrets.

Prefer environment configuration such as:

* `TEST_USERNAME`
* `TEST_PASSWORD`
* `TEST_ACCESS_TOKEN`
* `TEST_API_KEY`

Follow existing project conventions where available.

# PUBLIC endpoints

For an intentionally public endpoint, test:

## Without credentials

Send the request without authentication.

Verify:

* authentication is not required
* the request reaches application behavior
* the documented success or application-level response is returned

Where useful, also call the endpoint with valid credentials and verify that authentication does not break otherwise public access.

# AUTHENTICATED endpoints

At minimum, test three authentication states.

## No credentials

Send the request without credentials.

Verify the application's documented unauthenticated response.

This will commonly be:

`401 Unauthorized`

but do not assume `401` when the API contract specifies otherwise.

## Invalid credentials

Where practical, test one or more of:

* malformed credential
* invalid token
* expired token
* incorrect API key
* unusable session

Verify that authentication is rejected.

Do not create fragile tests that depend on undocumented token internals.

## Valid credentials

Acquire a valid test identity through the supported test mechanism.

Call the endpoint with valid authentication.

Verify the documented application behavior.

# AUTHORIZED endpoints

When an endpoint also requires a role, permission, scope, ownership rule, or tenant boundary, test:

1. unauthenticated request
2. authenticated but unauthorized request
3. authenticated and authorized request

For authenticated-but-unauthorized requests, expect the API's documented authorization response.

This will commonly be:

`403 Forbidden`

but use the application's contract rather than assuming it.

# Ownership and tenant boundaries

Where applicable, test that a valid user cannot improperly access:

* another user's resource
* another tenant's resource
* an administrative resource
* an endpoint outside their granted scope

Prefer test-created resources rather than existing arbitrary data.

# Authentication assertions

Validate more than a single HTTP code when useful.

Possible assertions include:

* HTTP status
* error response schema
* authentication error code
* absence of protected response data
* expected `WWW-Authenticate` behavior when documented

Do not assert sensitive credential values.

# Security-sensitive failures

Do not weaken a failing authentication test merely because the current implementation behaves differently.

Classify the failure as one of:

* test defect
* specification/implementation mismatch
* authentication defect
* authorization defect
* environment/configuration problem

Fix test defects.

Report application defects and contract mismatches.

