from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from ..database import get_db_session
from ..dependencies import get_current_user
from ..models.test_result import TestResult
from ..models.analyte import AnalyteCatalog, ReferenceRange
from ..models.family import FamilyMember
from ..schemas.results import TestResultSchema, TimeSeriesResponseSchema, TimeSeriesSeries, TimeSeriesDatapoint

router = APIRouter()


@router.get("", response_model=list[TestResultSchema])
async def get_results(
    family_member_id: str = Query(...),
    analyte_id: list[str] | None = Query(None),
    category: str | None = Query(None),
    date_from: str | None = Query(None),
    date_to: str | None = Query(None),
    db: AsyncSession = Depends(get_db_session),
    current_user = Depends(get_current_user),
):
    """Get test results for a family member."""
    query = select(TestResult).where(
        TestResult.family_member_id == family_member_id
    )

    # Filter by analyte IDs if provided
    if analyte_id:
        query = query.where(TestResult.analyte_id.in_(analyte_id))

    # Filter by category if provided
    if category:
        query = query.join(AnalyteCatalog).where(
            AnalyteCatalog.category == category
        )

    # Filter by date range
    if date_from:
        try:
            from_date = datetime.fromisoformat(date_from).date()
            query = query.where(TestResult.report_date >= from_date)
        except ValueError:
            pass

    if date_to:
        try:
            to_date = datetime.fromisoformat(date_to).date()
            query = query.where(TestResult.report_date <= to_date)
        except ValueError:
            pass

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/timeseries", response_model=TimeSeriesResponseSchema)
async def get_timeseries(
    family_member_id: str = Query(...),
    analyte_id: list[str] | None = Query(None),
    date_from: str | None = Query(None),
    date_to: str | None = Query(None),
    db: AsyncSession = Depends(get_db_session),
    current_user = Depends(get_current_user),
):
    """Get results in time-series format for charting."""
    # Get test results
    query = select(TestResult).where(
        TestResult.family_member_id == family_member_id
    )

    if analyte_id:
        query = query.where(TestResult.analyte_id.in_(analyte_id))

    if date_from:
        try:
            from_date = datetime.fromisoformat(date_from).date()
            query = query.where(TestResult.report_date >= from_date)
        except ValueError:
            pass

    if date_to:
        try:
            to_date = datetime.fromisoformat(date_to).date()
            query = query.where(TestResult.report_date <= to_date)
        except ValueError:
            pass

    result = await db.execute(
        query.order_by(TestResult.report_date).options(selectinload(TestResult.analyte))
    )
    test_results = result.scalars().all()

    # Group by analyte
    series_map = {}
    for test_result in test_results:
        if test_result.analyte_id not in series_map:
            series_map[test_result.analyte_id] = {
                "analyte": test_result.analyte,
                "datapoints": [],
            }

        series_map[test_result.analyte_id]["datapoints"].append(test_result)

    # Get family member's sex for sex-specific range lookup
    member_result = await db.execute(select(FamilyMember).where(FamilyMember.id == family_member_id))
    member = member_result.scalar_one_or_none()
    member_sex = member.sex if member else None

    # Fetch reference ranges — sex-specific (if member sex known) and sex-neutral
    sex_filter = (
        or_(ReferenceRange.sex == member_sex, ReferenceRange.sex.is_(None))
        if member_sex
        else ReferenceRange.sex.is_(None)
    )
    rr_result = await db.execute(
        select(ReferenceRange).where(
            ReferenceRange.analyte_id.in_(list(series_map.keys())),
            sex_filter,
        )
    )
    # Prefer sex-specific over sex-neutral when both exist
    ref_ranges: dict[str, ReferenceRange] = {}
    for rr in rr_result.scalars().all():
        if rr.analyte_id not in ref_ranges or rr.sex is not None:
            ref_ranges[rr.analyte_id] = rr

    # Build response
    series = []
    for analyte_id, data in series_map.items():
        analyte = data["analyte"]
        rr = ref_ranges.get(analyte_id)
        ref_low = rr.low_normal if rr else None
        ref_high = rr.high_normal if rr else None

        datapoints = [
            TimeSeriesDatapoint(
                date=str(tr.report_date) if tr.report_date else "",
                value=tr.canonical_value,
                ref_low=ref_low,
                ref_high=ref_high,
            )
            for tr in data["datapoints"]
        ]

        series.append(TimeSeriesSeries(
            analyte_id=analyte.id,
            analyte_name=analyte.canonical_name,
            unit=analyte.canonical_unit,
            category=analyte.category,
            ref_low=ref_low,
            ref_high=ref_high,
            datapoints=datapoints,
        ))

    return TimeSeriesResponseSchema(series=series)


@router.patch("/{id}", response_model=TestResultSchema)
async def patch_result(
    id: str,
    db: AsyncSession = Depends(get_db_session),
    current_user = Depends(get_current_user),
):
    """Manually correct a test result."""
    test_result = await db.get(TestResult, id)
    if not test_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test result not found",
        )

    # TODO: implement manual correction
    return test_result


@router.delete("/{id}")
async def delete_result(
    id: str,
    db: AsyncSession = Depends(get_db_session),
    current_user = Depends(get_current_user),
):
    """Delete a test result."""
    test_result = await db.get(TestResult, id)
    if not test_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test result not found",
        )

    await db.delete(test_result)
    await db.commit()

    return {"message": "Test result deleted"}
