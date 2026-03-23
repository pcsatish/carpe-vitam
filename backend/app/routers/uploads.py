from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db_session
from ..dependencies import get_current_user
from ..models.lab_report import LabReport
from ..schemas.uploads import LabReportSchema, UploadResponseSchema, SetReportDateSchema
from ..services.upload_service import UploadService, DuplicateUploadError
from ..services.result_service import ResultService

router = APIRouter()


@router.post("", response_model=UploadResponseSchema)
async def upload_pdf(
    file: UploadFile = File(...),
    family_member_id: str = Form(...),
    report_date: Optional[date] = Form(None),
    db: AsyncSession = Depends(get_db_session),
    current_user=Depends(get_current_user),
):
    """Upload a lab report PDF."""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported",
        )

    try:
        content = await file.read()
        upload_service = UploadService()
        lab_report = await upload_service.receive_upload(
            db=db,
            file_content=content,
            filename=file.filename,
            family_member_id=family_member_id,
            uploaded_by_user_id=current_user.id,
            report_date=report_date,
        )

        # Trigger extraction synchronously (Phase 3 will use async queue)
        result_service = ResultService()
        lab_report = await result_service.extract_and_persist(
            db=db,
            lab_report_id=lab_report.id,
            file_path=lab_report.storage_path,
        )

        return UploadResponseSchema(
            lab_report_id=lab_report.id,
            extraction_status=lab_report.extraction_status,
            report_date=lab_report.report_date,
            message="File uploaded successfully",
        )
    except DuplicateUploadError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}",
        )


@router.get("", response_model=list[LabReportSchema])
async def list_uploads(
    family_member_id: str | None = Query(None),
    db: AsyncSession = Depends(get_db_session),
    current_user=Depends(get_current_user),
):
    """List uploaded lab reports."""
    query = select(LabReport).where(LabReport.is_deleted.is_(False))

    if family_member_id:
        query = query.where(LabReport.family_member_id == family_member_id)

    result = await db.execute(query)
    reports = result.scalars().all()
    return reports


@router.get("/{id}", response_model=LabReportSchema)
async def get_upload(
    id: str,
    db: AsyncSession = Depends(get_db_session),
    current_user=Depends(get_current_user),
):
    """Get a specific upload details."""
    lab_report = await db.get(LabReport, id)
    if not lab_report or lab_report.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lab report not found",
        )
    return lab_report


@router.patch("/{id}/date", response_model=LabReportSchema)
async def set_report_date(
    id: str,
    payload: SetReportDateSchema,
    db: AsyncSession = Depends(get_db_session),
    current_user=Depends(get_current_user),
):
    """Set the report date on a lab report and backfill test result report_dates."""
    lab_report = await db.get(LabReport, id)
    if not lab_report or lab_report.is_deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lab report not found")

    lab_report.report_date = payload.report_date
    # Backfill report_date on all test results for this report
    from sqlalchemy import update
    from ..models.test_result import TestResult

    await db.execute(
        update(TestResult)
        .where(TestResult.lab_report_id == id)
        .values(report_date=payload.report_date)
    )
    await db.commit()
    await db.refresh(lab_report)
    return lab_report


@router.delete("/{id}")
async def delete_upload(
    id: str,
    db: AsyncSession = Depends(get_db_session),
    current_user=Depends(get_current_user),
):
    """Delete a lab report."""
    upload_service = UploadService()
    success = await upload_service.delete_upload(db, id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lab report not found",
        )
    return {"message": "Lab report deleted"}
