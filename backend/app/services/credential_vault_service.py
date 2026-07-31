"""
====================================================================
Project : AEGIS
System  : Autonomous Enterprise Global Intelligence System
Company : Honeydewnuts Nigerian Limited

File    : credential_vault_service.py

Purpose :
Enterprise Broker Credential Vault.

Current Stage:
CP-006 Batch 1
====================================================================
"""

from __future__ import annotations

import base64
import os
import secrets
from datetime import datetime
from typing import Any

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.core.logging import configure_logging


class CredentialVaultService:
    """
    Broker-agnostic credential vault.

    NOTE
    ----
    This implementation demonstrates the vault API.

    Storage is currently in-memory.

    A future batch will replace the internal dictionary with
    PostgreSQL while preserving this public interface.
    """

    def __init__(self) -> None:

        self.logger = configure_logging()

        self._vault: dict[str, dict[str, Any]] = {}

        key = os.getenv("AEGIS_MASTER_KEY")

        if key is None:
            raise RuntimeError(
                "AEGIS_MASTER_KEY environment variable is missing."
            )

        self._master_key = base64.b64decode(key)

        if len(self._master_key) != 32:
            raise RuntimeError(
                "AEGIS_MASTER_KEY must decode to exactly 32 bytes."
            )

        self._aes = AESGCM(self._master_key)

    # ---------------------------------------------------------

    def _encrypt(self, plaintext: str) -> dict[str, str]:

        nonce = secrets.token_bytes(12)

        ciphertext = self._aes.encrypt(
            nonce,
            plaintext.encode("utf-8"),
            None,
        )

        return {
            "nonce": base64.b64encode(nonce).decode(),
            "ciphertext": base64.b64encode(ciphertext).decode(),
        }

    def _decrypt(
        self,
        nonce: str,
        ciphertext: str,
    ) -> str:

        plain = self._aes.decrypt(
            base64.b64decode(nonce),
            base64.b64decode(ciphertext),
            None,
        )

        return plain.decode()

    # ---------------------------------------------------------

    def save_credentials(
        self,
        *,
        credential_id: str,
        broker_name: str,
        server: str,
        account_id: str,
        trading_password: str,
        investor_password: str | None,
        execution_enabled: bool,
    ) -> None:

        encrypted = self._encrypt(trading_password)

        self._vault[credential_id] = {

            "broker_name": broker_name,
            "server": server,
            "account_id": account_id,

            "nonce": encrypted["nonce"],
            "ciphertext": encrypted["ciphertext"],

            "investor_password": investor_password,

            "execution_enabled": execution_enabled,

            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

        self.logger.info(
            "Credential stored for account %s",
            account_id,
        )

    # ---------------------------------------------------------

    def get_credentials(
        self,
        credential_id: str,
    ) -> dict[str, Any]:

        if credential_id not in self._vault:
            raise KeyError("Credential not found.")

        record = self._vault[credential_id]

        self.logger.info(
            "Credential accessed: %s",
            credential_id,
        )

        if not record["execution_enabled"]:

            return {
                "broker_name": record["broker_name"],
                "server": record["server"],
                "account_id": record["account_id"],
                "execution_enabled": False,
            }

        password = self._decrypt(
            record["nonce"],
            record["ciphertext"],
        )

        return {
            "broker_name": record["broker_name"],
            "server": record["server"],
            "account_id": record["account_id"],
            "trading_password": password,
            "execution_enabled": True,
        }

    # ---------------------------------------------------------

    def get_credentials_by_account(
        self,
        account_id: str,
    ) -> dict[str, Any] | None:
        """
        Retrieve broker credentials using the broker account ID.

        Why this method exists
        ----------------------
        The BrokerConnectionService works with broker account IDs
        rather than internal vault credential IDs.

        The vault therefore performs the mapping from account_id
        to the corresponding credential record.

        Returns
        -------
        dict | None

        The returned dictionary is intentionally identical to
        get_credentials() so both lookup methods expose the same
        public contract.

        Returns None if the account cannot be found.
        """

        for _, record in self._vault.items():

            if record["account_id"] != account_id:
                continue

            self.logger.info(
                "Credential accessed by account_id: %s",
                account_id,
            )

            if not record["execution_enabled"]:

                return {
                    "broker_name": record["broker_name"],
                    "server": record["server"],
                    "account_id": record["account_id"],
                    "execution_enabled": False,
                }

            password = self._decrypt(
                record["nonce"],
                record["ciphertext"],
            )

            return {
                "broker_name": record["broker_name"],
                "server": record["server"],
                "account_id": record["account_id"],
                "trading_password": password,
                "execution_enabled": True,
            }

        return None

    # ---------------------------------------------------------

    def rotate_credentials(
        self,
        credential_id: str,
        new_password: str,
    ) -> None:

        record = self._vault[credential_id]

        encrypted = self._encrypt(new_password)

        record["nonce"] = encrypted["nonce"]
        record["ciphertext"] = encrypted["ciphertext"]
        record["updated_at"] = datetime.utcnow()

        self.logger.info(
            "Credential rotated: %s",
            credential_id,
        )

    # ---------------------------------------------------------

    def delete_credentials(
        self,
        credential_id: str,
    ) -> None:

        self._vault.pop(
            credential_id,
            None,
        )

        self.logger.info(
            "Credential deleted: %s",
            credential_id,
        )
