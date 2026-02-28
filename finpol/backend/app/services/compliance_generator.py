"""Compliance Generator Service - LLM-based compliance analysis.

This module provides:
- Async LLM generation support
- Abstraction for different LLM providers
- Easy integration with future ML models
- Prompt template management
"""
import logging
import asyncio
from typing import List, Optional
from abc import ABC, abstractmethod

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain.schema import HumanMessage, SystemMessage

from app.config import settings
from app.models.transaction_model import Transaction
from app.models.risk_response_model import RiskResult

logger = logging.getLogger(__name__)


# ============================================================
# System Prompts
# ============================================================

SYSTEM_PROMPT = """You are a fintech compliance officer with expertise in:
- Anti-Money Laundering (AML) regulations
- Know Your Customer (KYC) requirements
- RBI (Reserve Bank of India) guidelines
- FATF recommendations
- PCI-DSS standards

Generate audit-ready explanations for transaction risk assessments.
Provide clear, professional compliance documentation."""


ANALYSIS_PROMPT = """Transaction Details:
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


# ============================================================
# LLM Provider Protocol (for future multi-provider support)
# ============================================================

class LLMProvider(ABC):
    """Abstract protocol for LLM providers."""
    
    @abstractmethod
    async def generate(self, prompt: str) -> str:
        """Generate response from prompt."""
        pass
    
    @abstractmethod
    async def generate_with_messages(self, messages: list) -> str:
        """Generate response from messages."""
        pass


# ============================================================
# OpenAI LLM Provider Implementation
# ============================================================

class OpenAIProvider(LLMProvider):
    """OpenAI GPT provider implementation."""
    
    def __init__(self, model_name: str = None, api_key: str = None, temperature: float = 0.2):
        """
        Initialize OpenAI provider.
        
        Args:
            model_name: Model name (gpt-4, gpt-4-turbo, etc.)
            api_key: OpenAI API key
            temperature: Sampling temperature
        """
        self.model_name = model_name or settings.model_name
        self.api_key = api_key or settings.openai_api_key
        self.temperature = temperature
        self._llm = ChatOpenAI(
            model=self.model_name,
            temperature=self.temperature,
            api_key=self.api_key
        )
        logger.info(f"OpenAIProvider initialized with model: {self.model_name}")
    
    async def generate(self, prompt: str) -> str:
        """Generate response from prompt."""
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self._llm.invoke(prompt)
        )
        return response.content.strip()
    
    async def generate_with_messages(self, messages: list) -> str:
        """Generate response from messages."""
        loop = asyncio.get_event_loop()
        
        def _invoke():
            langchain_messages = []
            for msg in messages:
                if msg["role"] == "system":
                    langchain_messages.append(SystemMessage(content=msg["content"]))
                else:
                    langchain_messages.append(HumanMessage(content=msg["content"]))
            return self._llm.invoke(langchain_messages)
        
        response = await loop.run_in_executor(None, _invoke)
        return response.content.strip()


# ============================================================
# Compliance Generator Service
# ============================================================

class ComplianceGenerator:
    """
    Service for generating LLM-based compliance reports.
    
    Supports:
    - Async generation
    - Multiple LLM providers (via protocol)
    - Custom prompts
    - Error handling
    """
    
    def __init__(
        self,
        llm_provider: Optional[LLMProvider] = None,
        system_prompt: str = SYSTEM_PROMPT,
        analysis_prompt: str = ANALYSIS_PROMPT
    ):
        """
        Initialize the compliance generator.
        
        Args:
            llm_provider: Optional custom LLM provider
            system_prompt: System prompt for LLM
            analysis_prompt: Analysis prompt template
        """
        self._llm_provider = llm_provider or OpenAIProvider()
        self._system_prompt = system_prompt
        self._analysis_prompt = analysis_prompt
        logger.info("ComplianceGenerator initialized")
    
    def generate(
        self,
        transaction: Transaction,
        reasons: List[str],
        regulations: List[str]
    ) -> str:
        """
        Synchronous generation of compliance explanation.
        
        Args:
            transaction: The transaction to analyze
            reasons: List of risk factors identified
            regulations: List of relevant regulation texts
            
        Returns:
            Clean text compliance explanation
            
        Raises:
            RuntimeError: If LLM generation fails
        """
        return asyncio.get_event_loop().run_until_complete(
            self.generate_async(transaction, reasons, regulations)
        )
    
    async def generate_async(
        self,
        transaction: Transaction,
        reasons: List[str],
        regulations: List[str]
    ) -> str:
        """
        Asynchronous generation of compliance explanation.
        
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
            # Prepare transaction info
            transaction_info = self._format_transaction(transaction)
            reasons_text = "\n".join([f"- {r}" for r in reasons])
            regulations_text = "\n\n".join(regulations) if regulations else "No specific regulations found."
            
            # Format prompt
            human_prompt = self._analysis_prompt.format(
                transaction_info=transaction_info,
                reasons_text=reasons_text,
                regulations_text=regulations_text
            )
            
            # Generate response
            messages = [
                {"role": "system", "content": self._system_prompt},
                {"role": "human", "content": human_prompt}
            ]
            
            result = await self._llm_provider.generate_with_messages(messages)
            
            logger.info(
                f"Generated compliance explanation for transaction "
                f"{getattr(transaction, 'transaction_id', 'unknown')}"
            )
            return result
            
        except Exception as e:
            logger.error(f"Failed to generate compliance explanation: {e}")
            raise RuntimeError(f"Compliance generation failed: {e}")
    
    def _format_transaction(self, transaction: Transaction) -> str:
        """Format transaction for prompt."""
        return (
            f"Transaction ID: {getattr(transaction, 'transaction_id', 'N/A')}\n"
            f"User ID: {getattr(transaction, 'user_id', 'N/A')}\n"
            f"Amount: {transaction.amount}\n"
            f"Country: {transaction.country}\n"
            f"Merchant Type: {transaction.merchant_type}\n"
            f"Device Risk Score: {transaction.device_risk_score}"
        )
    
    async def generate_from_assessment(
        self,
        transaction: Transaction,
        assessment: RiskResult,
        regulations: List[str]
    ) -> str:
        """
        Generate compliance explanation from risk assessment.
        
        Args:
            transaction: The transaction
            assessment: RiskResult from risk engine
            regulations: List of relevant regulations
            
        Returns:
            Compliance explanation
        """
        return await self.generate_async(
            transaction,
            assessment.factors,
            regulations
        )
    
    def set_system_prompt(self, prompt: str) -> None:
        """Update system prompt."""
        self._system_prompt = prompt
        logger.info("System prompt updated")
    
    def set_analysis_prompt(self, prompt: str) -> None:
        """Update analysis prompt."""
        self._analysis_prompt = prompt
        logger.info("Analysis prompt updated")
