#!/usr/bin/env python3

import argparse
import os
import sys

HAS_AZURE_SDK = True
try:
    from azure.keyvault.secrets import SecretClient
    from azure.identity import DefaultAzureCredential
except ImportError:
    HAS_AZURE_SDK = False

HAS_DOTENV = True
try:
    from dotenv import load_dotenv
except ImportError:
    HAS_DOTENV = False


def set_secret(kv_endpoint, secret_name, secret_value, credential=None, client=None):
    if not kv_endpoint:
        raise ValueError("Key Vault endpoint is required")
    if not secret_name:
        raise ValueError("Secret name is required")
    if not secret_value:
        raise ValueError("Secret value is required")

    if not kv_endpoint.startswith("https://"):
        kv_endpoint = f"https://{kv_endpoint}"
    if not kv_endpoint.endswith("/"):
        kv_endpoint = kv_endpoint + "/"

    if client is None:
        if not HAS_AZURE_SDK:
            raise ImportError("azure-keyvault-secrets and azure-identity are required")
        if credential is None:
            credential = DefaultAzureCredential()
        client = SecretClient(vault_url=kv_endpoint, credential=credential)

    client.set_secret(secret_name, secret_value)
    return f"Successfully created secret: {secret_name} in keyvault: {kv_endpoint}"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Set a secret in Azure Key Vault"
    )

    parser.add_argument(
        "-n", "--secret-name",
        required=True,
        help="The name of the secret"
    )
    parser.add_argument(
        "-v", "--secret-value",
        required=False,
        default=None,
        help="The value of the secret (or set via SECRET_VALUE env var)"
    )
    parser.add_argument(
        "-e", "--kv-endpoint",
        required=False,
        default=None,
        help="Key Vault endpoint (or set via KV_ENDPOINT env var)"
    )
    parser.add_argument(
        "--env-var",
        required=False,
        default="storage_conn_string",
        help="Environment variable name to read secret value from (default: storage_conn_string)"
    )

    return parser.parse_args()


def main():
    if not HAS_AZURE_SDK:
        print("Error: Please install azure-keyvault-secrets and azure-identity")
        print("pip install azure-keyvault-secrets azure-identity")
        return 1

    if HAS_DOTENV:
        load_dotenv(override=True)

    args = parse_args()

    kv_endpoint = args.kv_endpoint or os.getenv("KV_ENDPOINT")
    if not kv_endpoint:
        print("Error: Key Vault endpoint is required.")
        print("Set via -e/--kv-endpoint argument or KV_ENDPOINT environment variable")
        return 1

    secret_value = args.secret_value or os.getenv("SECRET_VALUE") or os.getenv(args.env_var)
    if not secret_value:
        print(f"Error: Secret value is required.")
        print(f"Set via -v/--secret-value argument, SECRET_VALUE env var, or {args.env_var} env var")
        return 1

    try:
        message = set_secret(kv_endpoint, args.secret_name, secret_value)
        print(message)
        return 0
    except ValueError as e:
        print(f"Validation error: {e}")
        return 1
    except Exception as e:
        print(f"Error setting secret: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
