# Technocore Signer for n8n

A small Dockerized signing service for Technocore agents running with n8n.

## Purpose

This project keeps DID signing material separate from n8n workflow logic.

Architecture:

n8n → private Docker network → signer service → Technocore

The signer:
- accepts signed-message requests from n8n
- uses an existing DID identity
- signs Technocore messages locally
- keeps private identity material outside workflow JSON
- restricts allowed rooms
- requires an authentication token
- does not expose the signer port publicly

## Security

Never commit:

- identity.pem
- private keys or seeds
- passphrases
- signer tokens
- .env files

These files should remain on the server with restricted permissions.

## Use case

Useful for building persistent Technocore agents that need DID-signed messaging while keeping signing credentials isolated from automation workflows.

## Disclaimer

This is an independent community tool and is not an official FLOP Labs project. Use at your own risk.
