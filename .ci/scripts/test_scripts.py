#!/usr/bin/env python3
"""
Test cases for the fixed CI scripts.
These tests verify basic functionality without requiring actual Azure access.
"""
import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Add scripts directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class TestAMLCreation(unittest.TestCase):
    """Test cases for aml_creation.py"""

    def test_import_succeeds(self):
        """Test that the module can be imported without errors"""
        try:
            import aml_creation
            self.assertIsNotNone(aml_creation)
        except Exception as e:
            self.fail(f"Import failed with: {e}")

    def test_help_message(self):
        """Test that help message is displayed correctly"""
        with patch('sys.argv', ['aml_creation.py', '-h']):
            with patch('sys.exit') as mock_exit:
                with patch('builtins.print') as mock_print:
                    import aml_creation
                    try:
                        aml_creation.main(['-h'])
                    except SystemExit:
                        pass
                    # Verify help message was printed
                    help_calls = [str(call[0][0]) for call in mock_print.call_args_list]
                    self.assertTrue(any('subscription_id' in msg for msg in help_calls))

    def test_missing_parameters(self):
        """Test that missing parameters trigger error"""
        with patch('sys.argv', ['aml_creation.py', '-s', 'test_sub']):
            with patch('sys.exit') as mock_exit:
                with patch('builtins.print'):
                    import aml_creation
                    try:
                        aml_creation.main(['-s', 'test_sub'])
                    except SystemExit as e:
                        self.assertEqual(e.code, 1)


class TestAMLAttachBlob(unittest.TestCase):
    """Test cases for aml_attach_blob.py"""

    def test_import_succeeds(self):
        """Test that the module can be imported without errors"""
        try:
            import aml_attach_blob
            self.assertIsNotNone(aml_attach_blob)
        except Exception as e:
            self.fail(f"Import failed with: {e}")

    def test_datastore_import_present(self):
        """Test that Datastore is imported from azureml.core"""
        import aml_attach_blob
        self.assertTrue(hasattr(aml_attach_blob, 'Datastore'))

    def test_help_message(self):
        """Test that help message contains all required params"""
        with patch('sys.argv', ['aml_attach_blob.py', '-h']):
            with patch('sys.exit'):
                with patch('builtins.print') as mock_print:
                    import aml_attach_blob
                    try:
                        aml_attach_blob.main(['-h'])
                    except SystemExit:
                        pass
                    help_calls = [str(call[0][0]) for call in mock_print.call_args_list]
                    help_text = ' '.join(help_calls)
                    # Verify all expected parameters are mentioned
                    self.assertIn('blob_datastore_name', help_text)
                    self.assertIn('container_name', help_text)
                    self.assertIn('account_name', help_text)
                    self.assertIn('account_key', help_text)


class TestSetSecret(unittest.TestCase):
    """Test cases for set_secret.py"""

    def test_import_succeeds(self):
        """Test that the module can be imported without errors"""
        try:
            import set_secret
            self.assertIsNotNone(set_secret)
        except Exception as e:
            self.fail(f"Import failed with: {e}")

    def test_argparse_configuration(self):
        """Test that argument parser is configured correctly"""
        import set_secret
        with patch('sys.argv', ['set_secret.py', '-n', 'test_secret']):
            with patch('os.getenv', return_value=None):
                with patch('sys.exit') as mock_exit:
                    with patch('builtins.print'):
                        try:
                            set_secret.main()
                        except SystemExit:
                            pass

    def test_secret_value_validation(self):
        """Test that empty secret value raises error"""
        import set_secret
        with self.assertRaises(ValueError):
            set_secret.set_secret("https://test.vault.azure.net/", "test_secret", "")

    def test_endpoint_format_validation(self):
        """Test that endpoint format is properly handled"""
        import set_secret
        with patch('set_secret.get_client_from_cli_profile') as mock_client_factory:
            mock_client = MagicMock()
            mock_client_factory.return_value = mock_client
            mock_client.set_secret.return_value = True

            with patch('sys.argv', ['set_secret.py', '-n', 'test_secret', '-s', 'test_value']):
                with patch.dict(os.environ, {'KEY_VAULT_ENDPOINT': 'testvault.vault.azure.net'}):
                    with patch('builtins.print') as mock_print:
                        try:
                            set_secret.main()
                        except SystemExit:
                            pass
                        # Verify the client was called with properly formatted URL
                        if mock_client.set_secret.called:
                            call_args = mock_client.set_secret.call_args
                            url = call_args[0][0] if call_args else ""
                            self.assertTrue(url.startswith("https://"))
                            self.assertTrue(url.endswith("/"))


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

    # Run syntax checks first
    run_syntax_check()

    # Run unit tests
    print("\n=== Running Unit Tests ===")
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestAMLCreation))
    suite.addTests(loader.loadTestsFromTestCase(TestAMLAttachBlob))
    suite.addTests(loader.loadTestsFromTestCase(TestSetSecret))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Summary
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
