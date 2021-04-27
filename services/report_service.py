import datetime
from typing import List

import uuid as uuid

from models.Report import Report
from models.location import Location

__reports: List[Report] = []


async def get_reports() -> List[Report]:
    return list(__reports)


async def add_report(description: str, location: Location) -> Report:
    time = datetime.datetime.now()
    report = Report(id=str(uuid.uuid4()),
                    description=description,
                    location=location,
                    created_date=time)

    __reports.append(report)
    __reports.sort(key=lambda r: r.created_date, reverse=True)

    return report
