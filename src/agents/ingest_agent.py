"""Ingestion and Validation Agent for FinAgent-Ops."""

import logging
from typing import Any, Dict, List, Tuple

import pandas as pd
from pydantic import ValidationError

from src.models import BankTransaction, LedgerTransaction

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("IngestAgent")


class IngestionAgent:
    """Agent for ingesting, validating, and normalizing financial data."""

    def __init__(self) -> None:
        """Initialize IngestionAgent."""
        pass

    def load_and_validate_ledger(
        self, file_path: str
    ) -> Tuple[List[Dict[str, Any]], List[str]]:
        """Load, validate, and normalize enterprise ledger data from CSV.

        Args:
            file_path: Path to ledger CSV file.

        Returns:
            Tuple of (validated transaction dicts, error messages).
        """
        errors: List[str] = []
        validated_records: List[Dict[str, Any]] = []

        try:
            df = pd.read_csv(file_path)
        except Exception as err:
            logger.error("Failed to read ledger CSV %s: %s", file_path, err)
            return [], [f"Ledger file read error: {str(err)}"]

        for idx, row in df.iterrows():
            row_dict = row.to_dict()
            try:
                amount = float(row_dict.get("amount", 0.0))
                currency = str(row_dict.get("currency", "USD")).upper().strip()
                date_str = str(row_dict.get("date", "")).strip()
                ref_id = str(row_dict.get("reference_id", "")).strip()
                vendor = str(row_dict.get("vendor", "")).strip()
                txn_id = str(
                    row_dict.get("transaction_id", f"TXN-{idx+1}")
                ).strip()
                desc = str(row_dict.get("description", "")).strip()

                record = LedgerTransaction(
                    transaction_id=txn_id,
                    date=date_str,
                    amount=amount,
                    currency=currency,
                    vendor=vendor,
                    description=desc,
                    reference_id=ref_id,
                )
                validated_records.append(record.model_dump())
            except ValidationError as ve:
                err_msg = f"Ledger Row {idx} validation error: {str(ve)}"
                logger.warning(err_msg)
                errors.append(err_msg)
            except Exception as e:
                err_msg = f"Ledger Row {idx} parsing error: {str(e)}"
                logger.warning(err_msg)
                errors.append(err_msg)

        logger.info(
            "Ledger Ingestion Complete: %d valid, %d errors.",
            len(validated_records),
            len(errors),
        )
        return validated_records, errors

    def load_and_validate_bank(
        self, file_path: str
    ) -> Tuple[List[Dict[str, Any]], List[str]]:
        """Load, validate, and normalize bank statement data from CSV.

        Args:
            file_path: Path to bank statement CSV file.

        Returns:
            Tuple of (validated bank transaction dicts, error messages).
        """
        errors: List[str] = []
        validated_records: List[Dict[str, Any]] = []

        try:
            df = pd.read_csv(file_path)
        except Exception as err:
            logger.error(
                "Failed to read bank statement CSV %s: %s", file_path, err
            )
            return [], [f"Bank statement file read error: {str(err)}"]

        for idx, row in df.iterrows():
            row_dict = row.to_dict()
            try:
                amount = float(row_dict.get("amount", 0.0))
                currency = str(row_dict.get("currency", "USD")).upper().strip()
                booking_date = str(row_dict.get("booking_date", "")).strip()
                ref_code = str(row_dict.get("reference_code", "")).strip()
                counterparty = str(row_dict.get("counterparty", "")).strip()
                bank_txn_id = str(
                    row_dict.get("bank_txn_id", f"BANK-{idx+1}")
                ).strip()
                status = str(row_dict.get("status", "POSTED")).strip()

                record = BankTransaction(
                    bank_txn_id=bank_txn_id,
                    booking_date=booking_date,
                    amount=amount,
                    currency=currency,
                    counterparty=counterparty,
                    reference_code=ref_code,
                    status=status,
                )
                validated_records.append(record.model_dump())
            except ValidationError as ve:
                err_msg = (
                    f"Bank Statement Row {idx} validation error: {str(ve)}"
                )
                logger.warning(err_msg)
                errors.append(err_msg)
            except Exception as e:
                err_msg = f"Bank Statement Row {idx} parsing error: {str(e)}"
                logger.warning(err_msg)
                errors.append(err_msg)

        logger.info(
            "Bank Statement Ingestion Complete: %d valid, %d errors.",
            len(validated_records),
            len(errors),
        )
        return validated_records, errors

    def process(
        self, ledger_file: str, bank_file: str
    ) -> Dict[str, Any]:
        """Execute ingestion pipeline for ledger and bank statements.

        Args:
            ledger_file: Path to ledger CSV.
            bank_file: Path to bank statement CSV.

        Returns:
            Dict containing normalized datasets and ingestion errors.
        """
        ledger_data, l_errors = self.load_and_validate_ledger(ledger_file)
        bank_data, b_errors = self.load_and_validate_bank(bank_file)

        return {
            "normalized_ledger": ledger_data,
            "normalized_bank": bank_data,
            "ingestion_errors": l_errors + b_errors,
        }
