"""PDF Report Generator Service - Creates downloadable compliance reports."""

import io
import logging
from typing import List, Dict, Any
from datetime import datetime
from collections import defaultdict

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, 
    PageBreak, Image, TableStyle
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY

from app.models.transaction_model import Transaction

logger = logging.getLogger(__name__)


class PDFReportGenerator:
    """
    Generates PDF compliance reports from analyzed transactions.
    
    Report includes:
    - Executive summary
    - Risk distribution
    - High/Critical transactions
    - Compliance recommendations
    """
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles."""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=30,
            alignment=TA_CENTER,
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1e293b'),
            spaceAfter=12,
            spaceBefore=20,
        ))
        
        self.styles.add(ParagraphStyle(
            name='NormalJustified',
            parent=self.styles['Normal'],
            alignment=TA_JUSTIFY,
            spaceAfter=10,
        ))
    
    def generate_compliance_report(
        self,
        transactions: List[Transaction],
        risk_results: Dict[str, Dict[str, Any]],
        regulations: List[Dict[str, Any]],
        output_filename: str = None
    ) -> bytes:
        """
        Generate a PDF compliance report.
        
        Args:
            transactions: List of transactions
            risk_results: Dict mapping transaction_id to risk assessment
            regulations: List of relevant regulations
            output_filename: Optional output filename
            
        Returns:
            PDF bytes
        """
        if output_filename is None:
            output_filename = f"compliance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72,
        )
        
        # Build content
        story = []
        
        # Title
        story.append(Paragraph("FinPol Compliance Report", self.styles['CustomTitle']))
        story.append(Spacer(1, 10))
        
        # Report metadata
        story.append(Paragraph(
            f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
            self.styles['Normal']
        ))
        story.append(Paragraph(
            f"Total Transactions Analyzed: {len(transactions)}",
            self.styles['Normal']
        ))
        story.append(Spacer(1, 20))
        
        # Executive Summary
        story.extend(self._build_executive_summary(transactions, risk_results))
        
        # Risk Distribution
        story.extend(self._build_risk_distribution(transactions, risk_results))
        
        # High Risk Transactions
        story.extend(self._build_high_risk_section(transactions, risk_results))
        
        # Critical Transactions
        story.extend(self._build_critical_section(transactions, risk_results))
        
        # Regulations Applied
        if regulations:
            story.extend(self._build_regulations_section(regulations))
        
        # Recommendations
        story.extend(self._build_recommendations_section(transactions, risk_results))
        
        # Build PDF
        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        logger.info(f"Generated PDF report: {output_filename} ({len(pdf_bytes)} bytes)")
        return pdf_bytes
    
    def _build_executive_summary(
        self,
        transactions: List[Transaction],
        risk_results: Dict[str, Dict[str, Any]]
    ) -> List:
        """Build executive summary section."""
        story = []
        
        story.append(Paragraph("Executive Summary", self.styles['SectionHeader']))
        
        # Calculate stats
        total = len(transactions)
        if total == 0:
            story.append(Paragraph("No transactions to report.", self.styles['Normal']))
            story.append(Spacer(1, 20))
            return story
        
        risk_counts = defaultdict(int)
        total_amount = 0
        
        for tx in transactions:
            result = risk_results.get(tx.transaction_id, {})
            level = result.get('risk_level', 'Low')
            risk_counts[level] += 1
            total_amount += tx.amount
        
        # Summary table
        summary_data = [
            ['Metric', 'Value'],
            ['Total Transactions', str(total)],
            ['Total Transaction Value', f"${total_amount:,.2f}"],
            ['Low Risk', str(risk_counts.get('Low', 0))],
            ['Medium Risk', str(risk_counts.get('Medium', 0))],
            ['High Risk', str(risk_counts.get('High', 0))],
            ['Critical Risk', str(risk_counts.get('Critical', 0))],
        ]
        
        table = Table(summary_data, colWidths=[3*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
        ]))
        story.append(table)
        story.append(Spacer(1, 20))
        
        return story
    
    def _build_risk_distribution(
        self,
        transactions: List[Transaction],
        risk_results: Dict[str, Dict[str, Any]]
    ) -> List:
        """Build risk distribution section."""
        story = []
        
        story.append(Paragraph("Risk Distribution Analysis", self.styles['SectionHeader']))
        
        total = len(transactions)
        if total == 0:
            story.append(Paragraph("No data available.", self.styles['Normal']))
            story.append(Spacer(1, 20))
            return story
        
        # Calculate percentages
        risk_counts = defaultdict(int)
        for tx in transactions:
            result = risk_results.get(tx.transaction_id, {})
            level = result.get('risk_level', 'Low')
            risk_counts[level] += 1
        
        risk_pct = {
            'Low': (risk_counts['Low'] / total) * 100,
            'Medium': (risk_counts['Medium'] / total) * 100,
            'High': (risk_counts['High'] / total) * 100,
            'Critical': (risk_counts['Critical'] / total) * 100,
        }
        
        # Risk level descriptions
        risk_descriptions = {
            'Low': 'Transactions within normal parameters',
            'Medium': 'Requires additional verification',
            'High': 'Requires manual review and approval',
            'Critical': 'Requires immediate investigation',
        }
        
        for level in ['Low', 'Medium', 'High', 'Critical']:
            count = risk_counts[level]
            pct = risk_pct[level]
            story.append(Paragraph(
                f"<b>{level}:</b> {count} transactions ({pct:.1f}%) - {risk_descriptions[level]}",
                self.styles['Normal']
            ))
            story.append(Spacer(1, 8))
        
        story.append(Spacer(1, 20))
        return story
    
    def _build_high_risk_section(
        self,
        transactions: List[Transaction],
        risk_results: Dict[str, Dict[str, Any]]
    ) -> List:
        """Build high risk transactions section."""
        story = []
        
        # Get high risk transactions
        high_risk = []
        for tx in transactions:
            result = risk_results.get(tx.transaction_id, {})
            if result.get('risk_level') in ['High', 'Critical']:
                high_risk.append((tx, result))
        
        if not high_risk:
            return story
        
        story.append(Paragraph("High Risk Transactions Requiring Attention", self.styles['SectionHeader']))
        story.append(Paragraph(
            f"The following {len(high_risk)} transaction(s) require immediate review:",
            self.styles['Normal']
        ))
        story.append(Spacer(1, 10))
        
        # Table of high risk transactions
        table_data = [
            ['Transaction ID', 'Amount', 'Type', 'Risk Level', 'Reason']
        ]
        
        for tx, result in high_risk[:20]:  # Limit to 20 for PDF size
            table_data.append([
                tx.transaction_id,
                f"${tx.amount:,.2f}",
                tx.transaction_type.value if hasattr(tx.transaction_type, 'value') else str(tx.transaction_type),
                result.get('risk_level', 'Unknown'),
                (result.get('reason', 'N/A') or 'N/A')[:40]
            ])
        
        if len(table_data) > 1:
            table = Table(table_data, colWidths=[1.3*inch, 1*inch, 0.8*inch, 0.9*inch, 1.5*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#dc2626')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#fef2f2')),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#fca5a5')),
            ]))
            story.append(table)
        
        if len(high_risk) > 20:
            story.append(Paragraph(
                f"... and {len(high_risk) - 20} more high risk transactions",
                self.styles['Normal']
            ))
        
        story.append(Spacer(1, 20))
        return story
    
    def _build_critical_section(
        self,
        transactions: List[Transaction],
        risk_results: Dict[str, Dict[str, Any]]
    ) -> List:
        """Build critical transactions section."""
        story = []
        
        critical = [
            (tx, result) for tx, result in [
                (tx, risk_results.get(tx.transaction_id, {}))
                for tx in transactions
            ]
            if result.get('risk_level') == 'Critical'
        ]
        
        if not critical:
            return story
        
        story.append(Paragraph("Critical Transactions - Immediate Action Required", self.styles['SectionHeader']))
        story.append(Paragraph(
            f"<b>⚠️ URGENT:</b> The following {len(critical)} transaction(s) require immediate investigation:",
            self.styles['Normal']
        ))
        story.append(Spacer(1, 10))
        
        for tx, result in critical:
            story.append(Paragraph(
                f"<b>{tx.transaction_id}</b> - ${tx.amount:,.2f} - {result.get('reason', 'No reason provided')}",
                self.styles['Normal']
            ))
            story.append(Spacer(1, 5))
        
        story.append(Spacer(1, 20))
        return story
    
    def _build_regulations_section(self, regulations: List[Dict[str, Any]]) -> List:
        """Build regulations applied section."""
        story = []
        
        story.append(Paragraph("Regulations Applied", self.styles['SectionHeader']))
        
        # Get unique regulations
        seen = set()
        unique_regs = []
        for reg in regulations:
            reg_id = reg.get('id', reg.get('title', 'unknown'))
            if reg_id not in seen:
                seen.add(reg_id)
                unique_regs.append(reg)
        
        for reg in unique_regs[:10]:  # Limit to 10
            title = reg.get('title', 'Unknown Regulation')
            content = reg.get('content', '')[:150]
            story.append(Paragraph(f"<b>{title}</b>", self.styles['Normal']))
            story.append(Paragraph(content + "...", self.styles['Normal']))
            story.append(Spacer(1, 8))
        
        if len(unique_regs) > 10:
            story.append(Paragraph(
                f"... and {len(unique_regs) - 10} more regulations",
                self.styles['Normal']
            ))
        
        story.append(Spacer(1, 20))
        return story
    
    def _build_recommendations_section(
        self,
        transactions: List[Transaction],
        risk_results: Dict[str, Dict[str, Any]]
    ) -> List:
        """Build recommendations section."""
        story = []
        
        story.append(Paragraph("Compliance Recommendations", self.styles['SectionHeader']))
        
        # Calculate recommendations based on risk distribution
        high_risk_count = sum(
            1 for tx in transactions
            if risk_results.get(tx.transaction_id, {}).get('risk_level') == 'High'
        )
        critical_count = sum(
            1 for tx in transactions
            if risk_results.get(tx.transaction_id, {}).get('risk_level') == 'Critical'
        )
        
        recommendations = []
        
        if critical_count > 0:
            recommendations.append(
                f"1. IMMEDIATE ACTION: {critical_count} critical transaction(s) require immediate "
                f"investigation for potential money laundering or fraud indicators."
            )
        
        if high_risk_count > 5:
            recommendations.append(
                f"2. ENHANCED DUE DILIGENCE: Review {high_risk_count} high-risk transactions "
                f"and consider filing Suspicious Activity Reports (SARs) where appropriate."
            )
        
        # Check for patterns
        amounts = [tx.amount for tx in transactions]
        if amounts:
            avg_amount = sum(amounts) / len(amounts)
            high_amounts = [a for a in amounts if a > avg_amount * 5]
            if len(high_amounts) > len(amounts) * 0.1:
                recommendations.append(
                    f"3. MONITORING: Consider implementing additional controls for transactions "
                    f"exceeding 5x the average amount (${avg_amount * 5:,.2f})."
                )
        
        # Check for crypto
        crypto_count = sum(
            1 for tx in transactions
            if tx.merchant_type == 'crypto_exchange'
        )
        if crypto_count > 0:
            recommendations.append(
                f"4. CRYPTOCURRENCY: {crypto_count} transaction(s) involve cryptocurrency exchanges. "
                f"Ensure enhanced monitoring per FATF Travel Rule requirements."
            )
        
        # Check for foreign transactions
        foreign_count = sum(
            1 for tx in transactions
            if tx.country and tx.country != 'India'
        )
        if foreign_count > len(transactions) * 0.2:
            recommendations.append(
                f"5. CROSS-BORDER: Significant volume of foreign transactions detected. "
                f"Ensure compliance with international sanctions and wire transfer rules."
            )
        
        if not recommendations:
            recommendations.append(
                "No significant concerns detected. Continue routine monitoring and compliance procedures."
            )
        
        for rec in recommendations:
            story.append(Paragraph(rec, self.styles['NormalJustified']))
            story.append(Spacer(1, 10))
        
        # Footer
        story.append(Spacer(1, 30))
        story.append(Paragraph(
            "---",
            self.styles['Normal']
        ))
        story.append(Paragraph(
            "This report was generated by FinPol - AI-Powered Financial Compliance System",
            self.styles['Normal']
        ))
        story.append(Paragraph(
            "For questions or concerns, contact your compliance officer.",
            self.styles['Normal']
        ))
        
        return story


# Singleton instance
report_generator = PDFReportGenerator()
