#!/usr/bin/env python3

import argparse
from azure.keyvault import KeyVaultClient
from azure.common.client_factory import get_client_from_cli_profile
from azure.common.credentials import ServicePrincipalCredentials
from dotenv import load_dotenv
import os


def set_secret(kv_endpoint, secret_name, secret_value):
    """Set a secret in Azure Key Vault."""
    if not secret_value:
        raise ValueError("Secret value cannot be empty or None")

    try:
        client = get_client_from_cli_profile(KeyVaultClient)
        client.set_secret(kv_endpoint, secret_name, secret_value)
        return (f"Successfully created secret: {secret_name} "
                f"in keyvault: {kv_endpoint}")
    except Exception as e:
        raise RuntimeError(f"Failed to set secret: {str(e)}")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Set a secret in Azure Key Vault"
    )

    parser.add_argument('-n', '--secretName', required=True,
                        help="The name of the secret")
    parser.add_argument('-v', '--vaultEndpoint',
                        help="The Key Vault endpoint URL (e.g., https://myvault.vault.azure.net/)")
    parser.add_argument('-e', '--envVar',
                        help="The name of the environment variable containing the secret value")
    parser.add_argument('-s', '--secretValue',
                        help="The secret value (not recommended, use env var instead)")

    return parser.parse_args()


def main():
    load_dotenv(override=True)

    args = parse_args()

    # Get Key Vault endpoint from args or environment
    kv_endpoint = args.vaultEndpoint or os.getenv("KEY_VAULT_ENDPOINT")
    if not kv_endpoint:
        print("Error: Key Vault endpoint not provided.")
        print("Use -v/--vaultEndpoint or set KEY_VAULT_ENDPOINT environment variable")
        return 1

    # Ensure proper endpoint format
    if not kv_endpoint.startswith("https://"):
        kv_endpoint = f"https://{kv_endpoint}"
    if not kv_endpoint.endswith("/"):
        kv_endpoint = f"{kv_endpoint}/"

    # Get secret value
    secret_value = None
    if args.secretValue:
        secret_value = args.secretValue
    elif args.envVar:
        secret_value = os.getenv(args.envVar)
        if not secret_value:
            print(f"Error: Environment variable {args.envVar} is not set")
            return 1
    else:
        # Default to storage_conn_string for backward compatibility
        secret_value = os.getenv("storage_conn_string")
        if not secret_value:
            print("Error: No secret value provided.")
            print("Use -s/--secretValue, -e/--envVar, or set storage_conn_string environment variable")
            return 1

    try:
        message = set_secret(kv_endpoint, args.secretName, secret_value)
        print(message)
        return 0
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1


if __name__ == "__main__":
    exit(main())
