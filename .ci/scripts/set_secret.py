#!/usr/bin/env python3

import argparse
from azure.keyvault import KeyVaultClient
from azure.common.client_factory import get_client_from_cli_profile
from dotenv import load_dotenv
import os
import sys


def set_secret(kv_endpoint, secret_name, secret_value):
    if not secret_value:
        raise ValueError("Secret value cannot be empty")
    
    client = get_client_from_cli_profile(KeyVaultClient)
    client.set_secret(kv_endpoint, secret_name, secret_value)
    return "Successfully created secret: {secret_name} in keyvault: {kv_endpoint}".format(
        secret_name=secret_name, kv_endpoint=kv_endpoint)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Set a secret in Azure Key Vault"
    )
    parser.add_argument('-n', '--secretName', required=True,
                        help="The name of the secret")
    parser.add_argument('-v', '--secretValue', required=False,
                        help="The value of the secret (if not provided, uses STORAGE_CONN_STRING env var)")
    parser.add_argument('-e', '--endpoint', required=False,
                        help="Key Vault endpoint URL (if not provided, uses KEY_VAULT_ENDPOINT env var)")
    return parser.parse_args()


def main():
    load_dotenv(override=True)
    
    args = parse_args()
    
    # Get endpoint from args or environment variable
    kv_endpoint = args.endpoint or os.getenv("KEY_VAULT_ENDPOINT")
    if not kv_endpoint:
        print("Error: Key Vault endpoint not provided. Use --endpoint or set KEY_VAULT_ENDPOINT env var.")
        sys.exit(1)
    
    # Ensure endpoint has proper format
    if not kv_endpoint.startswith("https://"):
        kv_endpoint = "https://" + kv_endpoint
    if not kv_endpoint.endswith("/"):
        kv_endpoint += "/"
    
    # Get secret value from args or environment variable
    secret_value = args.secretValue or os.getenv("STORAGE_CONN_STRING")
    if not secret_value:
        print("Error: Secret value not provided. Use --secretValue or set STORAGE_CONN_STRING env var.")
        sys.exit(1)
    
    try:
        message = set_secret(kv_endpoint, args.secretName, secret_value)
        print(message)
    except Exception as e:
        print(f"Error setting secret: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
