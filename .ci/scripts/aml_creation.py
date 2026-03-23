#!/usr/bin/env python3

import azureml.core
from azureml.core import Workspace
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

    try:
        opts, args = getopt.getopt(
            argv, "hs:rg:wn:wr:",
            ["subscription_id=", "resource_group=", "workspace_name=", "workspace_region="]
        )
    except getopt.GetoptError:
        print('aml_creation.py -s <subscription_id> -rg <resource_group> -wn <workspace_name> -wr <workspace_region>')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print('aml_creation.py -s <subscription_id> -rg <resource_group> -wn <workspace_name> -wr <workspace_region>')
            sys.exit()
        elif opt in ("-s", "--subscription_id"):
            subscription_id = arg
        elif opt in ("-rg", "--resource_group"):
            resource_group = arg
        elif opt in ("-wn", "--workspace_name"):
            workspace_name = arg
        elif opt in ("-wr", "--workspace_region"):
            workspace_region = arg

    # Validate required parameters
    if not all([subscription_id, resource_group, workspace_name, workspace_region]):
        print("Error: Missing required parameters")
        print('aml_creation.py -s <subscription_id> -rg <resource_group> -wn <workspace_name> -wr <workspace_region>')
        sys.exit(1)

    env_path = find_dotenv()
    if env_path == "":
        Path(".env").touch()
        env_path = find_dotenv()

    try:
        auth = get_auth(env_path)
        ws = Workspace.create(
            name=workspace_name,
            subscription_id=subscription_id,
            resource_group=resource_group,
            location=workspace_region,
            create_resource_group=True,
            auth=auth,
            exist_ok=True,
        )

        # Save workspace configuration to .env file
        set_key(env_path, "SUBSCRIPTION_ID", subscription_id)
        set_key(env_path, "RESOURCE_GROUP", resource_group)
        set_key(env_path, "WORKSPACE_NAME", workspace_name)
        set_key(env_path, "WORKSPACE_REGION", workspace_region)

        print(f"Successfully created/accessed workspace: {workspace_name}")
        print(f"Configuration saved to {env_path}")

    except Exception as e:
        print(f"Error creating workspace: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    print("AML SDK Version:", azureml.core.VERSION)
    main(sys.argv[1:])
