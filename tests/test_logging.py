"""Tests for odoo_boost.logging_config."""

from __future__ import annotations

import logging
import sys

from odoo_boost.logging_config import LOGGER_NAME, configure_logging


class TestConfigureLogging:
    def test_explicit_level(self):
        assert configure_logging("DEBUG") == logging.DEBUG
        assert logging.getLogger(LOGGER_NAME).level == logging.DEBUG

    def test_env_var_used_when_no_argument(self, monkeypatch):
        monkeypatch.setenv("ODOO_BOOST_LOG_LEVEL", "ERROR")
        assert configure_logging(None) == logging.ERROR

    def test_argument_beats_env(self, monkeypatch):
        monkeypatch.setenv("ODOO_BOOST_LOG_LEVEL", "ERROR")
        assert configure_logging("INFO") == logging.INFO

    def test_unknown_level_falls_back_to_warning(self):
        assert configure_logging("NOT_A_LEVEL") == logging.WARNING

    def test_handler_never_writes_to_stdout(self):
        """stdout is reserved for the stdio MCP protocol stream."""
        configure_logging("INFO")
        logger = logging.getLogger(LOGGER_NAME)
        assert logger.handlers
        for handler in logger.handlers:
            assert isinstance(handler, logging.StreamHandler)
            assert handler.stream is not sys.stdout
