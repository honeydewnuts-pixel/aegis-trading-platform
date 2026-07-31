"""
====================================================================
Project : AEGIS
System  : Autonomous Enterprise Global Intelligence System
Company : Honeydewnuts Nigerian Limited

File    : broker_adapter_interface.py

Purpose :
Defines the abstract Broker Adapter interface used throughout AEGIS.

Current Stage:
CP-006 – File 2

Overview
--------
AEGIS is designed to support multiple trading platforms:

    • MetaTrader 5
    • MetaTrader 4
    • cTrader
    • FIX Gateways
    • Binance
    • Bybit
    • Interactive Brokers
    • Future broker integrations

Rather than allowing the rest of the system to communicate directly
with any broker SDK, every broker implementation must inherit from
this interface.

This follows the Strategy Pattern.

Benefits
--------
• Broker-independent architecture
• Easier testing
• Easier maintenance
• New brokers can be added without modifying the core platform
• The BrokerConnectionService communicates only with this interface

Example
-------
BrokerConnectionService
            │
            ▼
      BrokerAdapter
      (this interface)
            │
    ┌───────┼──────────┐
    ▼       ▼          ▼
 MT5     cTrader     Binance
Adapter   Adapter     Adapter

====================================================================
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any


class BrokerAdapter(ABC):
    """
    Abstract Broker Adapter.

    Every supported broker implementation must inherit from this
    class and implement every abstract method.

    The rest of AEGIS must never depend on a specific broker SDK.
    It should depend only on this interface.
    """

    @abstractmethod
    async def connect(
        self,
        credentials: dict[str, Any],
    ) -> bool:
        """
        Establish a broker connection.

        Parameters
        ----------
        credentials
            Broker credentials supplied by the
            Credential Vault.

        Returns
        -------
        bool
            True if the connection succeeds.

        Raises
        ------
        Implementations may raise broker-specific exceptions
        when connection fails.
        """
        raise NotImplementedError

    @abstractmethod
    async def disconnect(self) -> bool:
        """
        Close the broker connection.

        Returns
        -------
        bool
            True if the connection was closed successfully.
        """
        raise NotImplementedError

    @abstractmethod
    async def is_connected(self) -> bool:
        """
        Determine whether the broker session is currently active.

        Returns
        -------
        bool
            True when connected.
        """
        raise NotImplementedError

    @abstractmethod
    async def reconnect(self) -> bool:
        """
        Re-establish a lost broker connection.

        Implementations may internally reuse cached credentials
        or connection information.

        Returns
        -------
        bool
            True if reconnection succeeds.
        """
        raise NotImplementedError
