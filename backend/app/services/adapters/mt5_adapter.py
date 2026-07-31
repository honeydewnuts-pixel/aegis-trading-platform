"""
====================================================================
Project : AEGIS
System  : Autonomous Enterprise Global Intelligence System
Company : Honeydewnuts Nigerian Limited

File    : mt5_adapter.py

Purpose
-------
Concrete implementation of the BrokerAdapter interface for the
official MetaTrader 5 Python package.

Current Stage:
CP-006

Educational Notes
-----------------
Why are initialize() and login() separate?

The MetaTrader5 Python package works in two stages:

1. mt5.initialize()

   Starts communication with the locally installed MetaTrader 5
   terminal.

2. mt5.login()

   Authenticates a specific trading account using the supplied
   broker credentials.

Keeping these two calls separate follows the official MT5 API and
provides clearer error handling.

IMPORTANT
---------
No other AEGIS module should import MetaTrader5 directly.

All MT5-specific logic belongs inside this adapter.
====================================================================
"""

from __future__ import annotations

from typing import Any

import MetaTrader5 as mt5

from app.core.broker_types import BrokerType
from app.core.logging import configure_logging
from app.services.broker_adapter_interface import BrokerAdapter


class MT5Adapter(BrokerAdapter):
    """
    Concrete BrokerAdapter implementation for MetaTrader 5.
    """

    def __init__(self) -> None:

        self.logger = configure_logging()

        self._broker_type = BrokerType.MT5

        self._connected: bool = False

        self._credentials: dict[str, Any] | None = None

    async def connect(
        self,
        credentials: dict[str, Any],
    ) -> bool:
        """
        Connect to a MetaTrader 5 account.

        Parameters
        ----------
        credentials
            Dictionary returned by CredentialVaultService.
        """

        self._credentials = credentials

        try:

            #
            # STEP 1
            # Initialise communication with the MT5 terminal.
            #
            if not mt5.initialize():

                self.logger.error(
                    "MT5 initialize() failed: %s",
                    mt5.last_error(),
                )

                return False

            #
            # STEP 2
            # Authenticate the trading account.
            #
            login_ok = mt5.login(
                login=int(credentials["account_id"]),
                password=credentials["trading_password"],
                server=credentials["server"],
            )

            if not login_ok:

                self.logger.error(
                    "MT5 login failed: %s",
                    mt5.last_error(),
                )

                mt5.shutdown()

                return False

            self._connected = True

            self.logger.info(
                "MT5 Login Success: %s",
                credentials["account_id"],
            )

            return True

        except Exception as exc:

            self.logger.exception(
                "Unexpected MT5 connection error: %s",
                exc,
            )

            try:
                mt5.shutdown()
            except Exception:
                pass

            self._connected = False

            return False

    async def disconnect(self) -> bool:
        """
        Close the MT5 terminal connection.
        """

        try:

            mt5.shutdown()

            self._connected = False

            self.logger.info(
                "MT5 disconnected."
            )

            return True

        except Exception as exc:

            self.logger.exception(
                "MT5 disconnect failed: %s",
                exc,
            )

            return False

    async def is_connected(self) -> bool:
        """
        Check whether the adapter is still connected.

        terminal_info() returns None when communication with the
        terminal has been lost.
        """

        try:

            return (
                self._connected
                and mt5.terminal_info() is not None
            )

        except Exception:

            return False

    async def reconnect(self) -> bool:
        """
        Reconnect using the previously cached credentials.

        No external component needs to provide credentials again.
        """

        if self._credentials is None:

            self.logger.warning(
                "Reconnect requested without cached credentials."
            )

            return False

        await self.disconnect()

        return await self.connect(
            self._credentials,
        )
