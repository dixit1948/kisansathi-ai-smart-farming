"""Scan (disease detection) router."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import structlog

from app.core.database import get_db
from app.api.deps import require_farmer
from app.models.user import User
from app.models.scan import Scan, ScanSeverity
from app.agents.pest_disease import run_pest_disease_agent
from app.services.upload import save_upload

logger = structlog.get_logger(__name__)
router = APIRouter()


@router.post("", status_code=201)
async def create_scan(
    image: UploadFile = File(...),
    crop: Optional[str] = Form(default=None),
    farm_id: Optional[str] = Form(default=None),
    language: str = Form(default="en"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_farmer),
):
    """Upload leaf image, run disease detection, return result."""
    # Validate and save image
    image_path, image_b64 = await save_upload(image, user.id)

    # Run pest/disease agent
    result = await run_pest_disease_agent(
        image_path=image_path,
        image_base64=image_b64,
        crop=crop,
        language=language,
    )

    # Persist scan
    severity_map = {"low": ScanSeverity.LOW, "medium": ScanSeverity.MEDIUM, "high": ScanSeverity.HIGH, "critical": ScanSeverity.CRITICAL}
    severity_str = result.extra.get("severity", "medium") if result.extra else "medium"
    severity = severity_map.get(severity_str.lower(), ScanSeverity.MEDIUM)

    scan = Scan(
        user_id=user.id,
        farm_id=farm_id,
        image_path=image_path,
        original_filename=image.filename,
        predicted_label=result.extra.get("predicted_label") if result.extra else None,
        confidence=result.confidence,
        severity=severity,
        treatment_steps=result.extra.get("treatment_steps") if result.extra else None,
        prevention_tips=result.extra.get("prevention_tips") if result.extra else None,
        sources=[s.model_dump() for s in result.sources],
        is_mock=result.is_mock,
    )
    db.add(scan)
    await db.commit()
    await db.refresh(scan)

    return {
        "scan_id": scan.id,
        "predicted_label": scan.predicted_label,
        "confidence": scan.confidence,
        "severity": scan.severity.value if scan.severity else None,
        "answer": result.answer,
        "treatment_steps": scan.treatment_steps,
        "prevention_tips": scan.prevention_tips,
        "sources": [s.model_dump() for s in result.sources],
        "is_mock": scan.is_mock,
        "created_at": scan.created_at.isoformat(),
    }


@router.get("")
async def list_scans(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_farmer),
    limit: int = 20,
    offset: int = 0,
):
    result = await db.execute(
        select(Scan).where(Scan.user_id == user.id)
        .order_by(Scan.created_at.desc()).limit(limit).offset(offset)
    )
    scans = result.scalars().all()
    return [
        {
            "id": s.id,
            "predicted_label": s.predicted_label,
            "confidence": s.confidence,
            "severity": s.severity.value if s.severity else None,
            "image_path": f"/api/v1/scan/{s.id}/image",
            "created_at": s.created_at.isoformat(),
        }
        for s in scans
    ]


@router.get("/{scan_id}")
async def get_scan(
    scan_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_farmer),
):
    res = await db.execute(select(Scan).where(Scan.id == scan_id))
    scan = res.scalar_one_or_none()
    if not scan or scan.user_id != user.id:
        raise HTTPException(404, detail={"code": "NOT_FOUND", "message": "Scan not found."})
    return {
        "id": scan.id,
        "predicted_label": scan.predicted_label,
        "confidence": scan.confidence,
        "severity": scan.severity.value if scan.severity else None,
        "treatment_steps": scan.treatment_steps,
        "prevention_tips": scan.prevention_tips,
        "sources": scan.sources,
        "is_mock": scan.is_mock,
        "created_at": scan.created_at.isoformat(),
    }
