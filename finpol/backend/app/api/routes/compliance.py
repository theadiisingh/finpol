"""Compliance API routes."""
from fastapi import APIRouter, HTTPException, Depends, Query, UploadFile, File, Form
from fastapi.responses import Response
from typing import List, Optional
from datetime import datetime
import logging

from app.models.risk_response_model import ComplianceReport
from app.dependencies import get_compliance_generator, get_regulation_retriever
from app.services.compliance_generator import ComplianceGenerator
from app.services.regulation_retriever import RegulationRetriever
from app.services.bulk_processor import bulk_processor

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/report/{transaction_id}", response_model=ComplianceReport)
async def generate_compliance_report(
    transaction_id: str,
    risk_score: int = Query(..., description="Risk score from transaction analysis"),
    risk_level: str = Query(..., description="Risk level from transaction analysis"),
    compliance_gen: ComplianceGenerator = Depends(get_compliance_generator)
):
    """Generate compliance report for a transaction."""
    # Create a minimal report without the actual transaction
    # In production, you'd fetch the full transaction from DB
    report = ComplianceReport(
        transaction_id=transaction_id,
        compliance_status="review_required" if risk_level in ["Medium", "High", "Critical"] else "approved",
        regulations_applied=["AML", "KYC"] if risk_level in ["Medium", "High", "Critical"] else [],
        violations=[],
        recommendations=["Manual review required"] if risk_level in ["Medium", "High", "Critical"] else ["Auto-approved"],
        llm_analysis="Compliance review pending due to risk level: " + risk_level,
        timestamp=datetime.now()
    )
    return report


@router.get("/regulations", response_model=List[dict])
async def list_regulations(
    retriever: RegulationRetriever = Depends(get_regulation_retriever)
):
    """List all available regulations."""
    try:
        return await retriever.get_all_regulations()
    except FileNotFoundError:
        # Return sample regulations if vectorstore not available
        return [
            {"id": "aml_001", "title": "Anti-Money Laundering Act", "content": "Financial institutions must report suspicious transactions over $10,000."},
            {"id": "kyc_001", "title": "Know Your Customer", "content": "Customer identity verification required for all accounts."},
            {"id": "fatf_001", "title": "FATF Guidelines", "content": "International standards for combating money laundering and terrorist financing."}
        ]


@router.post("/regulations/search")
async def search_regulations(
    query: str,
    retriever: RegulationRetriever = Depends(get_regulation_retriever)
):
    """Search regulations by query."""
    try:
        results = await retriever.search_regulations_async(query)
        return results
    except FileNotFoundError:
        # Return sample results if vectorstore not available
        logger.warning(f"Vectorstore not available, returning sample results for query: {query}")
        return [
            {"content": f"Sample regulation related to: {query}. In production, this would come from the FAISS vectorstore."}
        ]


@router.get("/health")
async def compliance_health():
    """Health check for compliance service."""
    return {"status": "operational", "service": "compliance"}


@router.post("/upload")
async def upload_transactions(
    file: UploadFile = File(...),
    user_id: str = Form(default="bulk_upload")
):
    """
    Upload a file (PDF/CSV/Excel) containing transactions.
    
    The system will:
    1. Parse the file and extract transactions
    2. Analyze each transaction with the RiskEngine
    3. Retrieve relevant regulations via RAG
    4. Generate a PDF compliance report
    
    Returns summary of analysis and allows PDF download.
    """
    logger.info(f"Received file upload: {file.filename}")
    
    # Validate file type
    allowed_extensions = ['.csv', '.xlsx', '.xls', '.pdf']
    file_ext = file.filename.lower().split('.')[-1]
    
    if f'.{file_ext}' not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    try:
        # Read file content
        content = await file.read()
        
        # Process the file
        result = await bulk_processor.process_file(
            file_content=content,
            filename=file.filename,
            user_id=user_id
        )
        
        return {
            "status": "success",
            "message": f"Successfully processed {result['summary']['total_transactions']} transactions",
            "filename": result['filename'],
            "processed_at": result['processed_at'],
            "summary": result['summary']
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing file: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


@router.post("/upload-with-report")
async def upload_transactions_with_report(
    file: UploadFile = File(...),
    user_id: str = Form(default="bulk_upload")
):
    """
    Upload a file and get the PDF report directly.
    
    Returns the PDF as a downloadable file.
    """
    logger.info(f"Received file upload with report: {file.filename}")
    
    # Validate file type
    allowed_extensions = ['.csv', '.xlsx', '.xls', '.pdf']
    file_ext = file.filename.lower().split('.')[-1]
    
    if f'.{file_ext}' not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    try:
        # Read file content
        content = await file.read()
        
        # Process the file
        result = await bulk_processor.process_file(
            file_content=content,
            filename=file.filename,
            user_id=user_id
        )
        
        # Generate filename for PDF
        pdf_filename = f"compliance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        return Response(
            content=result['pdf_report'],
            media_type='application/pdf',
            headers={
                'Content-Disposition': f'attachment; filename="{pdf_filename}"'
            }
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing file: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


@router.get("/report/download/{report_id}")
async def download_report(report_id: str):
    """
    Download a previously generated report.
    
    In production, this would retrieve the report from storage.
    For now, returns a placeholder.
    """
    # In production, you'd fetch from database or file storage
    raise HTTPException(status_code=404, detail="Report not found. Please upload a new file.")
