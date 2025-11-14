"""
Earnings Router
File: backend/app/routers/earnings.py
Handles agent earnings endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from app.models import models
from app.models.database import get_db
from app.routers.auth import get_current_user
from app.schemas import EarningsSummary, EarningOut
from typing import List

router = APIRouter(prefix="/earnings", tags=["earnings"])

@router.get("", response_model=EarningsSummary)
def get_earnings(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get earnings summary for the current authenticated agent.
    Returns total earnings, today, this week, this month, and total deliveries.
    """
    # Check if user is an agent
    if not current_user.is_agent:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only agents can access earnings"
        )
    
    # Get agent record
    agent = db.query(models.Agent).filter(models.Agent.user_id == current_user.id).first()
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent profile not found"
        )
    
    # Get all earnings for this agent
    all_earnings = db.query(models.Earning).filter(
        models.Earning.agent_id == agent.id
    ).all()
    
    # Calculate totals
    total_earnings = sum(e.amount for e in all_earnings)
    
    # Calculate time-based earnings
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=now.weekday())
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    today_earnings = sum(
        e.amount for e in all_earnings 
        if e.timestamp >= today_start
    )
    
    this_week_earnings = sum(
        e.amount for e in all_earnings 
        if e.timestamp >= week_start
    )
    
    this_month_earnings = sum(
        e.amount for e in all_earnings 
        if e.timestamp >= month_start
    )
    
    # Count total deliveries (earnings with order_id)
    total_deliveries = len([e for e in all_earnings if e.order_id is not None])
    
    return EarningsSummary(
        total_earnings=total_earnings,
        today_earnings=today_earnings,
        this_week_earnings=this_week_earnings,
        this_month_earnings=this_month_earnings,
        total_deliveries=total_deliveries
    )

@router.get("/history", response_model=List[EarningOut])
def get_earnings_history(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed earnings history for the current authenticated agent.
    """
    # Check if user is an agent
    if not current_user.is_agent:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only agents can access earnings"
        )
    
    # Get agent record
    agent = db.query(models.Agent).filter(models.Agent.user_id == current_user.id).first()
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent profile not found"
        )
    
    # Get all earnings ordered by timestamp (newest first)
    earnings = db.query(models.Earning).filter(
        models.Earning.agent_id == agent.id
    ).order_by(models.Earning.timestamp.desc()).all()
    
    return earnings
