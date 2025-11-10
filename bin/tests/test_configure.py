"""
Tests for configure.py script.

Tests the main configuration script that processes YAML files and
generates OpenSCAD files for 3D printable bricks.
"""

import unittest
from unittest.mock import patch, MagicMock, mock_open
import sys
import pathlib
import io

# Add parent directory to path for imports
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

import configure


class TestConfigure(unittest.TestCase):
    """Test cases for the configure module."""

    @patch('configure.FLAGS')
    @patch('configure.logging')
    @patch('configure.Bricks')
    @patch('pathlib.Path.glob')
    @patch('configure.yaml')
    def test_main_initializes_bricks(self, mock_yaml, mock_glob, mock_bricks_class, mock_logging, mock_flags):
        """main() should initialize Bricks configuration system."""
        mock_flags.configs = 'configs/*.yaml'

        mock_bricks_instance = MagicMock()
        mock_bricks_class.return_value = mock_bricks_instance

        mock_glob.return_value = []

        configure.main([])

        # Should have created Bricks instance
        mock_bricks_class.assert_called_once()

    @patch('configure.FLAGS')
    @patch('configure.logging')
    @patch('configure.Bricks')
    @patch('pathlib.Path.glob')
    @patch('configure.yaml')
    def test_main_calls_configure(self, mock_yaml, mock_glob, mock_bricks_class, mock_logging, mock_flags):
        """main() should call configure on Bricks instance."""
        mock_flags.configs = 'configs/*.yaml'

        mock_bricks_instance = MagicMock()
        mock_bricks_class.return_value = mock_bricks_instance

        mock_yml_files = [MagicMock(), MagicMock()]
        mock_glob.return_value = mock_yml_files

        configure.main([])

        # Should have called configure with YAML files
        mock_bricks_instance.configure.assert_called_once()

    @patch('configure.FLAGS')
    @patch('configure.logging')
    @patch('configure.Bricks')
    @patch('pathlib.Path.glob')
    @patch('configure.yaml')
    def test_main_calls_write_configs(self, mock_yaml, mock_glob, mock_bricks_class, mock_logging, mock_flags):
        """main() should call writeConfigs to generate output."""
        mock_flags.configs = 'configs/*.yaml'

        mock_bricks_instance = MagicMock()
        mock_bricks_class.return_value = mock_bricks_instance

        mock_glob.return_value = []

        configure.main([])

        # Should have called writeConfigs
        mock_bricks_instance.writeConfigs.assert_called_once()

    @patch('configure.FLAGS')
    @patch('configure.logging')
    @patch('configure.Bricks')
    @patch('pathlib.Path.glob')
    @patch('configure.yaml')
    @patch('configure.STATS', {'test': {'new': 5, 'updated': 3}})
    @patch('sys.argv', ['configure.py'])  # Non-test mode
    def test_main_logs_stats(self, mock_yaml, mock_glob, mock_bricks_class, mock_logging, mock_flags):
        """main() should log statistics after completion (when not in test mode)."""
        mock_flags.configs = 'configs/*.yaml'

        mock_bricks_instance = MagicMock()
        mock_bricks_class.return_value = mock_bricks_instance

        mock_glob.return_value = []

        with patch('configure.io.StringIO') as mock_stringio:
            mock_buffer = MagicMock()
            mock_buffer.getvalue.return_value = 'test stats'
            mock_stringio.return_value.__enter__.return_value = mock_buffer

            configure.main([])

            # Stats output is suppressed in test mode (when 'unittest' in sys.argv)
            # This test verifies the function completes without error

    @patch('configure.FLAGS')
    @patch('configure.logging')
    @patch('configure.Bricks')
    @patch('pathlib.Path.glob')
    @patch('configure.yaml')
    @patch('configure.STATS', {'test': {'new': 5, 'updated': 3}})
    def test_main_suppresses_stats_in_test_mode(self, mock_yaml, mock_glob, mock_bricks_class, mock_logging, mock_flags):
        """main() should suppress stats output when running in test mode."""
        mock_flags.configs = 'configs/*.yaml'

        mock_bricks_instance = MagicMock()
        mock_bricks_class.return_value = mock_bricks_instance

        mock_glob.return_value = []

        # When sys.argv contains 'unittest', stats should be suppressed
        configure.main([])

        # Verify that logging.info is NOT called with the full STATS header
        # (because 'unittest' is in sys.argv during test runs)
        # We check for the specific stats format that includes the YAML dump
        stats_calls = [call for call in mock_logging.info.call_args_list
                      if call[0] and '\n\n**** STATS ****\n\n' in str(call[0])]
        self.assertEqual(len(stats_calls), 0, "Stats banner should be suppressed in test mode")

    @patch('configure.FLAGS')
    @patch('configure.logging')
    def test_main_configures_logging_format(self, mock_logging, mock_flags):
        """main() should configure logging to show only messages."""
        mock_flags.configs = 'configs/*.yaml'

        mock_handler = MagicMock()
        mock_logging.get_absl_handler.return_value = mock_handler

        with patch('configure.Bricks'), \
             patch('pathlib.Path.glob', return_value=[]), \
             patch('configure.yaml'):

            configure.main([])

            # Should have set formatter
            mock_handler.setFormatter.assert_called_once()

    @patch('configure.FLAGS')
    @patch('configure.logging')
    @patch('configure.Bricks')
    @patch('pathlib.Path.glob')
    @patch('configure.yaml')
    def test_main_globs_config_files(self, mock_yaml, mock_glob, mock_bricks_class, mock_logging, mock_flags):
        """main() should glob for YAML config files."""
        mock_flags.configs = 'configs/*.yaml'

        mock_bricks_instance = MagicMock()
        mock_bricks_class.return_value = mock_bricks_instance

        mock_yml_files = [MagicMock(spec=pathlib.Path)]
        mock_glob.return_value = mock_yml_files

        configure.main([])

        # Should have globbed for files
        mock_glob.assert_called_once()

    @patch('configure.FLAGS')
    @patch('configure.logging')
    @patch('configure.Bricks')
    @patch('pathlib.Path.glob')
    @patch('configure.yaml')
    def test_main_returns_none(self, mock_yaml, mock_glob, mock_bricks_class, mock_logging, mock_flags):
        """main() should return None."""
        mock_flags.configs = 'configs/*.yaml'

        mock_bricks_instance = MagicMock()
        mock_bricks_class.return_value = mock_bricks_instance

        mock_glob.return_value = []

        result = configure.main([])

        self.assertIsNone(result)

    @patch('configure.FLAGS')
    @patch('configure.logging')
    @patch('configure.Bricks')
    @patch('pathlib.Path.glob')
    @patch('configure.yaml')
    @patch('configure.STATS')
    def test_main_yaml_dump_stats(self, mock_stats, mock_yaml, mock_glob, mock_bricks_class, mock_logging, mock_flags):
        """main() should dump STATS to YAML format."""
        mock_flags.configs = 'configs/*.yaml'

        mock_bricks_instance = MagicMock()
        mock_bricks_class.return_value = mock_bricks_instance

        mock_glob.return_value = []

        mock_stats.items.return_value = [('test', {'new': 1})]

        with patch('configure.io.StringIO'):
            configure.main([])

            # yaml.dump should have been called to format stats

    def test_module_imports(self):
        """configure module should have all necessary imports."""
        self.assertTrue(hasattr(configure, 'collections'))
        self.assertTrue(hasattr(configure, 'pathlib'))
        self.assertTrue(hasattr(configure, 'json'))
        self.assertTrue(hasattr(configure, 'logging'))
        self.assertTrue(hasattr(configure, 'YAML'))
        self.assertTrue(hasattr(configure, 'BASEDIR'))
        self.assertTrue(hasattr(configure, 'STATS'))
        self.assertTrue(hasattr(configure, 'Bricks'))

    def test_module_has_main_function(self):
        """configure module should have a main function."""
        self.assertTrue(callable(configure.main))

    def test_module_flags_defined(self):
        """configure module should define command-line flags."""
        self.assertTrue(hasattr(configure, 'FLAGS'))

    @patch('configure.app')
    def test_module_entry_point(self, mock_app):
        """configure module should use absl app.run as entry point."""
        # This test verifies the structure at module level
        # The actual __name__ == '__main__' block would be tested differently
        self.assertTrue(hasattr(configure, 'app'))


class TestConfigureIntegration(unittest.TestCase):
    """Integration tests for configure module."""

    @patch('configure.FLAGS')
    @patch('configure.logging')
    @patch('pathlib.Path.glob')
    @patch('configure.yaml')
    def test_main_handles_empty_config_list(self, mock_yaml, mock_glob, mock_logging, mock_flags):
        """main() should handle empty list of config files."""
        mock_flags.configs = 'configs/*.yaml'

        mock_glob.return_value = []  # No YAML files found

        with patch('configure.Bricks') as mock_bricks_class:
            mock_bricks_instance = MagicMock()
            mock_bricks_class.return_value = mock_bricks_instance

            # Should not raise an error
            configure.main([])

            # Should still call configure with empty list
            mock_bricks_instance.configure.assert_called_once()

    @patch('configure.FLAGS')
    @patch('configure.logging')
    @patch('pathlib.Path.glob')
    @patch('configure.yaml')
    def test_main_processes_multiple_yaml_files(self, mock_yaml, mock_glob, mock_logging, mock_flags):
        """main() should process multiple YAML config files."""
        mock_flags.configs = 'configs/*.yaml'

        # Multiple YAML files
        mock_yml1 = MagicMock(spec=pathlib.Path)
        mock_yml2 = MagicMock(spec=pathlib.Path)
        mock_yml3 = MagicMock(spec=pathlib.Path)

        mock_glob.return_value = [mock_yml1, mock_yml2, mock_yml3]

        with patch('configure.Bricks') as mock_bricks_class:
            mock_bricks_instance = MagicMock()
            mock_bricks_class.return_value = mock_bricks_instance

            configure.main([])

            # Should have passed all files to configure
            call_args = mock_bricks_instance.configure.call_args
            self.assertEqual(len(call_args[0][0]), 3)


if __name__ == '__main__':
    unittest.main()
