from typing import Optional, List

import fastapi
from fastapi import Depends

from models.Report import Report, ReportSubmittal
from models.location import Location
from models.validation_error import ValidationError
from services import report_service
from services.weather_service import get_report

router = fastapi.APIRouter()


@router.get('/api/weather/{city}')
async def weather(loc: Location = Depends(), units: Optional[str] = None):
    try:
        return await get_report(loc, units)
    except ValidationError as ve:
        return fastapi.Response(content=ve.error_msg, status_code=ve.status_code)
    except Exception as x:
        return fastapi.Response(content=str(x), status_code=500)


@router.get('/api/reports', name='all_reports', response_model=List[Report])
async def reports_get() -> List[Report]:
    return await report_service.get_reports()


@router.post('/api/reports', name='add_report', response_model=Report, status_code=201)
async def reports_post(report_submittal: ReportSubmittal) -> Report:
    return await report_service.add_report(report_submittal.description, report_submittal.location)


