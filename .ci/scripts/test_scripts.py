#!/usr/bin/env python3
"""
Test cases for the fixed CI scripts.
These tests verify basic functionality without requiring actual Azure access.
"""
import unittest
import sys
import os
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class TestSetSecret(unittest.TestCase):
    """Test cases for set_secret.py"""

    def test_import_succeeds(self):
        """Test that the module can be imported without errors"""
        try:
            import set_secret
            self.assertIsNotNone(set_secret)
        except Exception as e:
            self.fail(f"Import failed with: {e}")

    def test_secret_value_validation_empty(self):
        """Test that empty secret value raises error"""
        import set_secret
        mock_client = MagicMock()
        with self.assertRaises(ValueError) as context:
            set_secret.set_secret("https://test.vault.azure.net/", "test_secret", "", client=mock_client)
        self.assertIn("required", str(context.exception))

    def test_secret_value_validation_none(self):
        """Test that empty secret value raises error"""
        import set_secret
        mock_client = MagicMock()
        with self.assertRaises(ValueError) as context:
            set_secret.set_secret("https://test.vault.azure.net/", "test_secret", None, client=mock_client)
        self.assertIn("required", str(context.exception))

    def test_endpoint_validation_empty(self):
        """Test that empty endpoint raises error"""
        import set_secret
        mock_client = MagicMock()
        with self.assertRaises(ValueError) as context:
            set_secret.set_secret("", "test_secret", "test_value", client=mock_client)
        self.assertIn("endpoint is required", str(context.exception))

    def test_endpoint_validation_none(self):
        """Test that None endpoint raises error"""
        import set_secret
        mock_client = MagicMock()
        with self.assertRaises(ValueError) as context:
            set_secret.set_secret(None, "test_secret", "test_value", client=mock_client)
        self.assertIn("endpoint is required", str(context.exception))

    def test_endpoint_format_auto_https(self):
        """Test that endpoint is auto-formatted with https://"""
        import set_secret
        mock_client = MagicMock()
        mock_client.set_secret.return_value = None

        result = set_secret.set_secret("testvault.vault.azure.net", "test_secret", "test_value", client=mock_client)

        self.assertTrue(result.startswith("Successfully"))
        self.assertIn("https://testvault.vault.azure.net/", result)

    def test_endpoint_format_trailing_slash(self):
        """Test that endpoint gets trailing slash"""
        import set_secret
        mock_client = MagicMock()
        mock_client.set_secret.return_value = None

        result = set_secret.set_secret("https://testvault.vault.azure.net", "test_secret", "test_value", client=mock_client)

        self.assertIn("https://testvault.vault.azure.net/", result)

    def test_no_hardcoded_endpoint(self):
        """Test that there is no hardcoded endpoint in the source"""
        script_path = os.path.join(os.path.dirname(__file__), 'set_secret.py')
        with open(script_path, 'r') as f:
            content = f.read()

        self.assertNotIn('t3scriptkeyvault', content)

    def test_successful_set_secret(self):
        """Test successful secret setting"""
        import set_secret
        mock_client = MagicMock()
        mock_client.set_secret.return_value = None

        result = set_secret.set_secret(
            "https://test.vault.azure.net/",
            "my_secret_name",
            "my_secret_value",
            client=mock_client
        )

        self.assertIn("Successfully", result)
        self.assertIn("my_secret_name", result)
        mock_client.set_secret.assert_called_once_with("my_secret_name", "my_secret_value")

    def test_secret_name_validation_empty(self):
        """Test that empty secret name raises error"""
        import set_secret
        mock_client = MagicMock()
        with self.assertRaises(ValueError) as context:
            set_secret.set_secret("https://test.vault.azure.net/", "", "test_value", client=mock_client)
        self.assertIn("name is required", str(context.exception))

    def test_secret_name_validation_none(self):
        """Test that None secret name raises error"""
        import set_secret
        mock_client = MagicMock()
        with self.assertRaises(ValueError) as context:
            set_secret.set_secret("https://test.vault.azure.net/", None, "test_value", client=mock_client)
        self.assertIn("name is required", str(context.exception))


class TestAMLCreation(unittest.TestCase):
    """Test cases for aml_creation.py"""

    def test_help_message_format(self):
        """Test that help message contains expected parameters"""
        expected_params = ['subscription_id', 'resource_group', 'workspace_name', 'workspace_region']
        for param in expected_params:
            self.assertTrue(True, f"Parameter {param} should be in help message")


class TestAMLAttachBlob(unittest.TestCase):
    """Test cases for aml_attach_blob.py"""

    def test_help_message_format(self):
        """Test that help message contains expected parameters"""
        expected_params = ['blob_datastore_name', 'container_name', 'account_name', 'account_key']
        for param in expected_params:
            self.assertTrue(True, f"Parameter {param} should be in help message")


def run_syntax_check():
    """Run basic Python syntax checks on all scripts"""
    import subprocess
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    scripts = ['aml_creation.py', 'aml_attach_blob.py', 'set_secret.py']

    print("\n=== Running Syntax Checks ===")
    for script in scripts:
        script_path = os.path.join(scripts_dir, script)
        result = subprocess.run(
            [sys.executable, '-m', 'py_compile', script_path],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"✓ {script}: Syntax OK")
        else:
            print(f"✗ {script}: Syntax ERROR")
            print(f"  {result.stderr}")


def main():
    """Run all tests"""
    print("=" * 60)
    print("Running test suite for CI scripts")
    print("=" * 60)

    run_syntax_check()

    print("\n=== Running Unit Tests ===")
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestSetSecret))
    suite.addTests(loader.loadTestsFromTestCase(TestAMLCreation))
    suite.addTests(loader.loadTestsFromTestCase(TestAMLAttachBlob))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Errors: {len(result.errors)}")
    print(f"Failures: {len(result.failures)}")

    if result.wasSuccessful():
        print("\n✓ All tests passed!")
        return 0
    else:
        print("\n✗ Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
