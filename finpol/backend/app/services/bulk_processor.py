"""Bulk Transaction Processing Service - Orchestrates the full compliance flow."""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from collections import defaultdict

from app.models.transaction_model import Transaction
from app.services.transaction_parser import parser as transaction_parser
from app.services.risk_engine import RiskEngine
from app.services.regulation_retriever import RegulationRetriever
from app.services.pdf_report_generator import report_generator

logger = logging.getLogger(__name__)


class BulkProcessor:
    """
    Orchestrates bulk transaction processing flow:
    1. Parse uploaded file (PDF/CSV/Excel)
    2. Analyze each transaction with RiskEngine
    3. Retrieve relevant regulations via RAG
    4. Generate PDF compliance report
    """
    
    def __init__(
        self,
        risk_engine: Optional[RiskEngine] = None,
        regulation_retriever: Optional[RegulationRetriever] = None
    ):
        self.risk_engine = risk_engine or RiskEngine()
        self.regulation_retriever = regulation_retriever or RegulationRetriever()
    
    async def process_file(
        self,
        file_content: bytes,
        filename: str,
        user_id: str = "bulk_upload"
    ) -> Dict[str, Any]:
        """
        Process uploaded file and return analysis results + PDF report.
        
        Args:
            file_content: Raw file bytes
            filename: Original filename
            user_id: User performing the upload
            
        Returns:
            Dict with analysis results and PDF report
        """
        logger.info(f"Processing file: {filename}")
        
        # Step 1: Parse the file
        parsed_data = transaction_parser.parse_file(file_content, filename)
        
        if not parsed_data:
            raise ValueError("No transactions found in the uploaded file")
        
        logger.info(f"Parsed {len(parsed_data)} transactions from file")
        
        # Step 2: Create Transaction objects
        transactions = transaction_parser.create_transactions(parsed_data, user_id)
        
        # Step 3: Analyze each transaction
        risk_results = await self._analyze_transactions(transactions)
        
        # Step 4: Get relevant regulations
        regulations = await self._get_relevant_regulations(transactions, risk_results)
        
        # Step 5: Generate PDF report
        pdf_bytes = report_generator.generate_compliance_report(
            transactions=transactions,
            risk_results=risk_results,
            regulations=regulations
        )
        
        # Step 6: Compile summary
        summary = self._compile_summary(transactions, risk_results)
        
        logger.info(f"Bulk processing complete: {len(transactions)} transactions analyzed")
        
        return {
            "transactions": transactions,
            "risk_results": risk_results,
            "regulations": regulations,
            "pdf_report": pdf_bytes,
            "summary": summary,
            "filename": filename,
            "processed_at": datetime.now().isoformat()
        }
    
    async def _analyze_transactions(
        self,
        transactions: List[Transaction]
    ) -> Dict[str, Dict[str, Any]]:
        """Analyze all transactions with RiskEngine."""
        results = {}
        
        for tx in transactions:
            try:
                assessment = await self.risk_engine.assess_risk_async(tx)
                results[tx.transaction_id] = {
                    "risk_score": assessment.risk_score,
                    "risk_level": assessment.risk_level,
                    "should_approve": assessment.should_approve,
                    "requires_review": assessment.requires_review,
                    "reasons": assessment.risk_factors if hasattr(assessment, 'risk_factors') else []
                }
            except Exception as e:
                logger.error(f"Error analyzing transaction {tx.transaction_id}: {e}")
                results[tx.transaction_id] = {
                    "risk_score": 0,
                    "risk_level": "Unknown",
                    "should_approve": False,
                    "requires_review": True,
                    "reasons": [f"Analysis error: {str(e)}"]
                }
        
        return results
    
    async def _get_relevant_regulations(
        self,
        transactions: List[Transaction],
        risk_results: Dict[str, Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Get relevant regulations based on high-risk transactions."""
        # Get unique risk factors
        risk_factors = set()
        for result in risk_results.values():
            level = result.get('risk_level', '')
            if level in ['High', 'Critical']:
                risk_factors.add('high_risk')
            if 'crypto' in str(result.get('reasons', [])).lower():
                risk_factors.add('cryptocurrency')
        
        # Query regulations based on risk factors
        regulations = []
        
        if 'high_risk' in risk_factors:
            try:
                regs = await self.regulation_retriever.search_regulations_async(
                    "anti-money laundering suspicious transactions reporting"
                )
                regulations.extend(regs)
            except Exception as e:
                logger.warning(f"Error retrieving AML regulations: {e}")
        
        if 'cryptocurrency' in risk_factors:
            try:
                regs = await self.regulation_retriever.search_regulations_async(
                    "cryptocurrency virtual assets FATF travel rule"
                )
                regulations.extend(regs)
            except Exception as e:
                logger.warning(f"Error retrieving crypto regulations: {e}")
        
        # Remove duplicates
        seen = set()
        unique_regulations = []
        for reg in regulations:
            reg_id = reg.get('id', reg.get('content', '')[:30])
            if reg_id not in seen:
                seen.add(reg_id)
                unique_regulations.append(reg)
        
        return unique_regulations
    
    def _compile_summary(
        self,
        transactions: List[Transaction],
        risk_results: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Compile summary statistics."""
        total = len(transactions)
        total_amount = sum(tx.amount for tx in transactions)
        
        risk_counts = defaultdict(int)
        risk_amounts = defaultdict(float)
        
        for tx in transactions:
            result = risk_results.get(tx.transaction_id, {})
            level = result.get('risk_level', 'Low')
            risk_counts[level] += 1
            risk_amounts[level] += tx.amount
        
        return {
            "total_transactions": total,
            "total_amount": total_amount,
            "risk_distribution": dict(risk_counts),
            "amount_by_risk": {k: float(v) for k, v in risk_amounts.items()},
            "compliance_rate": (
                (risk_counts.get('Low', 0) / total * 100) if total > 0 else 100
            ),
            "high_risk_count": risk_counts.get('High', 0),
            "critical_count": risk_counts.get('Critical', 0),
            "medium_risk_count": risk_counts.get('Medium', 0),
            "low_risk_count": risk_counts.get('Low', 0),
        }


# Singleton instance
bulk_processor = BulkProcessor()
