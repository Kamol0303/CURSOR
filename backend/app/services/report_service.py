import io
from datetime import UTC, datetime

from openpyxl import Workbook
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.identity import User
from app.models.ratings_certs import Report
from app.services.audit_service import write_audit_log
from app.services.rating_service import get_latest_ratings


async def generate_ratings_report(
    db: AsyncSession,
    user: User,
    *,
    file_format: str,
    locale: str,
    ip_address: str | None,
) -> tuple[bytes, str, str]:
    ratings = await get_latest_ratings(db, limit=100)
    content_type = "application/pdf"
    filename = f"tamor-ratings-{datetime.now(UTC).strftime('%Y%m%d')}.pdf"

    if file_format == "excel":
        content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        filename = filename.replace(".pdf", ".xlsx")
        buf = io.BytesIO()
        wb = Workbook()
        ws = wb.active
        ws.title = "Ratings"
        headers = ["Rank", "Center", "Score", "Rank Change"]
        ws.append(headers)
        for r in ratings:
            center_name = r.center.name if r.center else ""
            ws.append([r.rank, center_name, r.total_score, r.rank_change or "—"])
        wb.save(buf)
        data = buf.getvalue()
    else:
        buf = io.BytesIO()
        c = canvas.Canvas(buf, pagesize=A4)
        width, height = A4
        c.setFillColor(colors.HexColor("#1B4D3E"))
        c.setFont("Helvetica-Bold", 18)
        c.drawString(30 * mm, height - 30 * mm, "TaMoR — Center Ratings Report")
        c.setFont("Helvetica", 10)
        c.drawString(30 * mm, height - 38 * mm, datetime.now(UTC).strftime("%d.%m.%Y"))
        y = height - 55 * mm
        c.setFont("Helvetica-Bold", 11)
        c.drawString(20 * mm, y, "#")
        c.drawString(35 * mm, y, "Center")
        c.drawString(120 * mm, y, "Score")
        c.drawString(150 * mm, y, "Change")
        y -= 8 * mm
        c.setFont("Helvetica", 10)
        for r in ratings:
            if y < 30 * mm:
                c.showPage()
                y = height - 30 * mm
            center_name = (r.center.name if r.center else "")[:40]
            change = f"+{r.rank_change}" if r.rank_change and r.rank_change > 0 else str(r.rank_change or "—")
            c.drawString(20 * mm, y, str(r.rank))
            c.drawString(35 * mm, y, center_name)
            c.drawString(120 * mm, y, f"{r.total_score:.1f}")
            c.drawString(150 * mm, y, change)
            y -= 7 * mm
        c.save()
        data = buf.getvalue()

    report = Report(
        report_type="ratings",
        requested_by=user.id,
        parameters={"locale": locale, "count": len(ratings)},
        locale=locale,
        file_format=file_format,
        status="completed",
    )
    db.add(report)
    await db.flush()
    await write_audit_log(
        db,
        user_id=user.id,
        action="report.generate",
        resource_type="report",
        resource_id=report.id,
        ip_address=ip_address,
        details={"type": "ratings", "format": file_format},
    )
    return data, content_type, filename
