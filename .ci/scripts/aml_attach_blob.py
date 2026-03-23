#!/usr/bin/env python3

import azureml.core
from azureml.core import Workspace, Datastore
from dotenv import set_key, find_dotenv
from pathlib import Path
import sys
import getopt

try:
    from AIHelpers.utilities import get_auth
except ImportError:
    # Fallback if AIHelpers is not available
    get_auth = lambda x: None


def main(argv):
    subscription_id = None
    resource_group = None
    workspace_name = None
    workspace_region = None
    blob_datastore_name = None
    container_name = None
    account_name = None
    account_key = None
    datastore_rg = None

    try:
        opts, args = getopt.getopt(
            argv, "hs:rg:wn:wr:dsn:cn:an:ak:drg:",
            ["subscription_id=", "resource_group=", "workspace_name=", "workspace_region=",
             "blob_datastore_name=", "container_name=", "account_name=", "account_key=",
             "datastore_rg="]
        )
    except getopt.GetoptError:
        print('aml_attach_blob.py -s <subscription_id> -rg <resource_group> -wn <workspace_name> '
              '-wr <workspace_region> -dsn <blob_datastore_name> -cn <container_name> '
              '-an <account_name> -ak <account_key> [-drg <datastore_rg>]')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print('aml_attach_blob.py -s <subscription_id> -rg <resource_group> -wn <workspace_name> '
                  '-wr <workspace_region> -dsn <blob_datastore_name> -cn <container_name> '
                  '-an <account_name> -ak <account_key> [-drg <datastore_rg>]')
            sys.exit()
        elif opt in ("-s", "--subscription_id"):
            subscription_id = arg
        elif opt in ("-rg", "--resource_group"):
            resource_group = arg
        elif opt in ("-wn", "--workspace_name"):
            workspace_name = arg
        elif opt in ("-wr", "--workspace_region"):
            workspace_region = arg
        elif opt in ("-dsn", "--blob_datastore_name"):
            blob_datastore_name = arg
        elif opt in ("-cn", "--container_name"):
            container_name = arg
        elif opt in ("-an", "--account_name"):
            account_name = arg
        elif opt in ("-ak", "--account_key"):
            account_key = arg
        elif opt in ("-drg", "--datastore_rg"):
            datastore_rg = arg

    # Validate required parameters
    required_params = [subscription_id, resource_group, workspace_name,
                       workspace_region, blob_datastore_name, container_name,
                       account_name, account_key]
    if not all(required_params):
        print("Error: Missing required parameters")
        print('aml_attach_blob.py -s <subscription_id> -rg <resource_group> -wn <workspace_name> '
              '-wr <workspace_region> -dsn <blob_datastore_name> -cn <container_name> '
              '-an <account_name> -ak <account_key> [-drg <datastore_rg>]')
        sys.exit(1)

    env_path = find_dotenv()
    if env_path == "":
        Path(".env").touch()
        env_path = find_dotenv()

    try:
        auth = get_auth(env_path) if get_auth is not None else None
        ws = Workspace.create(
            name=workspace_name,
            subscription_id=subscription_id,
            resource_group=resource_group,
            location=workspace_region,
            create_resource_group=True,
            auth=auth,
            exist_ok=True,
        )

        blob_datastore = Datastore.register_azure_blob_container(
            workspace=ws,
            datastore_name=blob_datastore_name,
            container_name=container_name,
            account_name=account_name,
            account_key=account_key,
            resource_group=datastore_rg
        )

        # Save datastore configuration to .env file
        set_key(env_path, "BLOB_DATASTORE_NAME", blob_datastore_name)
        set_key(env_path, "CONTAINER_NAME", container_name)
        set_key(env_path, "ACCOUNT_NAME", account_name)

        print(f"Successfully registered blob datastore: {blob_datastore_name}")
        print(f"Configuration saved to {env_path}")

    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    print("AML SDK Version:", azureml.core.VERSION)
    main(sys.argv[1:])
