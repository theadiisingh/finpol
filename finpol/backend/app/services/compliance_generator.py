"""Compliance Generator Service - LLM-based compliance analysis."""
import logging
from typing import List

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

from app.config import settings
from app.models.transaction_model import Transaction

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """You are a fintech compliance officer.
Generate audit-ready explanations for transaction risk assessments.
Provide clear, professional compliance documentation."""


class ComplianceGenerator:
    """Service for generating LLM-based compliance reports."""
    
    def __init__(self):
        """Initialize the compliance generator with ChatOpenAI."""
        self.llm = ChatOpenAI(
            model=settings.model_name,
            temperature=0.2,
            api_key=settings.openai_api_key
        )
    
    def generate(
        self,
        transaction: Transaction,
        reasons: List[str],
        regulations: List[str]
    ) -> str:
        """
        Generate audit-ready compliance explanation.
        
        Args:
            transaction: The transaction to analyze
            reasons: List of risk factors identified
            regulations: List of relevant regulation texts
            
        Returns:
            Clean text compliance explanation
            
        Raises:
            RuntimeError: If LLM generation fails
        """
        try:
            transaction_info = (
                f"Transaction ID: {transaction.transaction_id}\n"
                f"User ID: {transaction.user_id}\n"
                f"Amount: {transaction.amount}\n"
                f"Country: {transaction.country}\n"
                f"Merchant Type: {transaction.merchant_type}\n"
                f"Device Risk Score: {transaction.device_risk_score}"
            )
            
            reasons_text = "\n".join([f"- {r}" for r in reasons])
            regulations_text = "\n\n".join(regulations)
            
            human_template = f"""Transaction Details:
{transaction_info}

Risk Factors Identified:
{reasons_text}

Relevant Regulations:
{regulations_text}

Generate an audit-ready compliance explanation that:
1. Summarizes the transaction risk assessment
2. Explains how each risk factor was evaluated
3. References applicable regulatory requirements
4. Provides a clear compliance determination

Provide clean, professional text suitable for audit documentation."""

            prompt = ChatPromptTemplate.from_messages([
                ("system", SYSTEM_PROMPT),
                ("human", human_template)
            ])
            
            chain = prompt | self.llm
            response = chain.invoke({})
            
            result = response.content.strip()
            logger.info(f"Generated compliance explanation for transaction {transaction.transaction_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to generate compliance explanation: {e}")
            raise RuntimeError(f"Compliance generation failed: {e}")
