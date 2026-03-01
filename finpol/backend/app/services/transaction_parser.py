"""Transaction Parser Service - Handles PDF, CSV, and Excel file parsing."""

import io
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import csv

import pandas as pd
from PyPDF2 import PdfReader

from app.models.transaction_model import Transaction, TransactionType

logger = logging.getLogger(__name__)


class TransactionParser:
    """
    Parses various file formats to extract transaction data.
    
    Supported formats:
    - CSV files
    - Excel files (.xlsx, .xls)
    - PDF files (bank statements)
    """
    
    # Common column mappings for different formats
    COLUMN_MAPPINGS = {
        'amount': ['amount', 'amt', 'value', 'transaction_amount', 'debit', 'credit', 'transaction_value'],
        'user_id': ['user_id', 'userid', 'customer_id', 'customerid', 'account_holder', 'user'],
        'currency': ['currency', 'curr', 'currency_code'],
        'transaction_type': ['type', 'transaction_type', 'txn_type', 'transaction_category'],
        'description': ['description', 'desc', 'memo', 'narration', 'details', 'particulars'],
        'recipient_account': ['recipient', 'beneficiary', 'to_account', 'receiver', 'destination_account'],
        'sender_account': ['sender', 'from_account', 'source_account', 'payer'],
        'country': ['country', 'country_code', 'nation'],
        'merchant_type': ['merchant', 'merchant_type', 'category', 'merchant_category', 'mcc'],
        'timestamp': ['date', 'timestamp', 'transaction_date', 'date_time', 'txn_date', 'value_date'],
    }
    
    def parse_file(self, file_content: bytes, filename: str) -> List[Dict[str, Any]]:
        """
        Parse a file and extract transactions.
        
        Args:
            file_content: Raw file content
            filename: Name of the file (determines parser)
            
        Returns:
            List of transaction dictionaries
        """
        file_ext = filename.lower().split('.')[-1]
        
        logger.info(f"Parsing file: {filename} (extension: {file_ext})")
        
        if file_ext == 'csv':
            return self._parse_csv(file_content)
        elif file_ext in ['xlsx', 'xls']:
            return self._parse_excel(file_content)
        elif file_ext == 'pdf':
            return self._parse_pdf(file_content)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")
    
    def _parse_csv(self, file_content: bytes) -> List[Dict[str, Any]]:
        """Parse CSV file."""
        try:
            df = pd.read_csv(io.BytesIO(file_content))
            return self._normalize_dataframe(df)
        except Exception as e:
            logger.error(f"Error parsing CSV: {e}")
            raise ValueError(f"Failed to parse CSV file: {str(e)}")
    
    def _parse_excel(self, file_content: bytes) -> List[Dict[str, Any]]:
        """Parse Excel file."""
        try:
            # Try reading all sheets
            df = pd.read_excel(io.BytesIO(file_content), sheet_name=0)
            return self._normalize_dataframe(df)
        except Exception as e:
            logger.error(f"Error parsing Excel: {e}")
            raise ValueError(f"Failed to parse Excel file: {str(e)}")
    
    def _parse_pdf(self, file_content: bytes) -> List[Dict[str, Any]]:
        """Parse PDF bank statement (basic text extraction)."""
        try:
            reader = PdfReader(io.BytesIO(file_content))
            transactions = []
            
            for page in reader.pages:
                text = page.extract_text()
                # Simple pattern matching for transactions
                # In production, you'd use more sophisticated parsing
                lines = text.split('\n')
                for line in lines:
                    # Look for lines with amounts (e.g., "$1,234.56" or "1,234.56")
                    if self._looks_like_transaction(line):
                        tx = self._extract_transaction_from_line(line)
                        if tx:
                            transactions.append(tx)
            
            logger.info(f"Extracted {len(transactions)} transactions from PDF")
            return transactions
        except Exception as e:
            logger.error(f"Error parsing PDF: {e}")
            raise ValueError(f"Failed to parse PDF file: {str(e)}")
    
    def _looks_like_transaction(self, line: str) -> bool:
        """Check if a line looks like a transaction."""
        # Look for currency patterns
        import re
        # Match patterns like $1,234.56 or 1234.56
        return bool(re.search(r'[\$€£]?\d{1,3}(?:,\d{3})*(?:\.\d{2})?', line))
    
    def _extract_transaction_from_line(self, line: str) -> Optional[Dict[str, Any]]:
        """Extract transaction data from a text line."""
        import re
        
        # Try to extract amount
        amount_match = re.search(r'[\$€£]?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)', line)
        if not amount_match:
            return None
        
        amount_str = amount_match.group(1).replace(',', '')
        try:
            amount = float(amount_str)
        except ValueError:
            return None
        
        # Try to extract date (common formats)
        date_match = re.search(r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})', line)
        timestamp = datetime.now()
        if date_match:
            try:
                timestamp = datetime.strptime(date_match.group(1), '%m/%d/%Y')
            except:
                try:
                    timestamp = datetime.strptime(date_match.group(1), '%d/%m/%Y')
                except:
                    pass
        
        # Determine if debit or credit
        is_debit = 'debit' in line.lower() or 'dr' in line.lower()
        
        return {
            'amount': amount,
            'transaction_type': 'withdrawal' if is_debit else 'deposit',
            'description': line.strip()[:200],  # Limit description length
            'timestamp': timestamp.isoformat(),
            'currency': 'USD',
            'country': 'Unknown',
            'merchant_type': 'retail',
            'device_risk_score': 0.0,
        }
    
    def _normalize_dataframe(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Normalize dataframe columns to standard transaction format."""
        transactions = []
        
        # Rename columns to standard names
        df.columns = df.columns.str.lower().str.strip()
        
        for _, row in df.iterrows():
            tx = self._normalize_row(row)
            if tx:
                transactions.append(tx)
        
        logger.info(f"Normalized {len(transactions)} transactions from dataframe")
        return transactions
    
    def _normalize_row(self, row: pd.Series) -> Optional[Dict[str, Any]]:
        """Normalize a single row to standard transaction format."""
        tx = {}
        
        for standard_field, possible_columns in self.COLUMN_MAPPINGS.items():
            for col in possible_columns:
                if col in row.index:
                    value = row[col]
                    if pd.notna(value):
                        tx[standard_field] = value
                        break
        
        # Ensure required fields
        if 'amount' not in tx:
            return None
        
        # Set defaults
        tx.setdefault('currency', 'USD')
        tx.setdefault('country', 'India')
        tx.setdefault('merchant_type', 'retail')
        tx.setdefault('device_risk_score', 0.0)
        tx.setdefault('timestamp', datetime.now().isoformat())
        tx.setdefault('transaction_type', 'transfer')
        
        # Convert amount to float
        try:
            tx['amount'] = float(tx['amount'])
        except:
            return None
        
        return tx
    
    def create_transactions(self, data: List[Dict[str, Any]], user_id: str = "bulk_upload") -> List[Transaction]:
        """
        Create Transaction objects from parsed data.
        
        Args:
            data: List of transaction dictionaries
            user_id: Default user ID for transactions
            
        Returns:
            List of Transaction objects
        """
        transactions = []
        
        for idx, item in enumerate(data):
            try:
                # Generate transaction ID
                txn_id = f"TXN-{datetime.now().strftime('%Y%m%d')}-{idx+1:04d}"
                
                # Parse timestamp
                timestamp = item.get('timestamp')
                if isinstance(timestamp, str):
                    try:
                        timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    except:
                        timestamp = datetime.now()
                elif timestamp is None:
                    timestamp = datetime.now()
                
                # Determine transaction type
                txn_type = item.get('transaction_type', 'transfer')
                if isinstance(txn_type, str):
                    try:
                        txn_type = TransactionType(txn_type.lower())
                    except:
                        txn_type = TransactionType.TRANSFER
                
                tx = Transaction(
                    transaction_id=txn_id,
                    user_id=item.get('user_id', user_id),
                    amount=float(item['amount']),
                    currency=item.get('currency', 'USD'),
                    country=item.get('country', 'India'),
                    merchant_type=item.get('merchant_type', 'retail'),
                    device_risk_score=float(item.get('device_risk_score', 0.0)),
                    timestamp=timestamp,
                    transaction_type=txn_type,
                    description=item.get('description'),
                    recipient_account=item.get('recipient_account'),
                    sender_account=item.get('sender_account'),
                )
                transactions.append(tx)
                
            except Exception as e:
                logger.warning(f"Failed to create transaction from row {idx}: {e}")
                continue
        
        logger.info(f"Created {len(transactions)} Transaction objects from {len(data)} records")
        return transactions


# Singleton instance
parser = TransactionParser()
