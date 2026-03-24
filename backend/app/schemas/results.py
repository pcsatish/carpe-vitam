"""Result schemas for API responses."""

from datetime import datetime
from pydantic import BaseModel


class TestResultSchema(BaseModel):
    """Single test result."""

    id: str
    analyte_id: str
    raw_name: str
    canonical_value: float | None
    canonical_unit: str
    report_date: datetime | None
    is_out_of_range: bool

    class Config:
        from_attributes = True


class TimeSeriesDatapoint(BaseModel):
    """Single datapoint in a time-series."""

    date: str
    value: float | None
    ref_low: float | None
    ref_high: float | None
    lab_name: str | None


class TimeSeriesSeries(BaseModel):
    """Time-series data for a single analyte."""

    analyte_id: str
    analyte_name: str
    unit: str
    category: str | None
    ref_low: float | None
    ref_high: float | None
    datapoints: list[TimeSeriesDatapoint]


class TimeSeriesResponseSchema(BaseModel):
    """Response for time-series endpoint."""

    series: list[TimeSeriesSeries]
