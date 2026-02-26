"""Celery task worker for asynchronous processing"""

import os
import uuid
from datetime import datetime
from dotenv import load_dotenv
from celery import Celery
from sqlalchemy.orm import Session

load_dotenv()

# Celery configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
BROKER_URL = os.getenv("BROKER_URL", REDIS_URL)
RESULT_BACKEND = os.getenv("RESULT_BACKEND", REDIS_URL)

# Initialize Celery
celery_app = Celery(__name__)
celery_app.conf.broker_url = BROKER_URL
celery_app.conf.result_backend = RESULT_BACKEND
celery_app.conf.accept_content = ["json"]
celery_app.conf.task_serializer = "json"
celery_app.conf.result_serializer = "json"
celery_app.conf.timezone = "UTC"
celery_app.conf.task_track_started = True
celery_app.conf.task_time_limit = 30 * 60  # 30 minutes


@celery_app.task(bind=True, name="analyze_document_async")
def analyze_document_task(self, file_path: str, query: str, analysis_id: str):
    """
    Asynchronous task to analyze financial document
    
    Args:
        file_path: Path to the uploaded document
        query: User's analysis query
        analysis_id: UUID for tracking this analysis
        
    Returns:
        dict: Analysis results with status and data
    """
    try:
        from crewai import Crew, Process
        from agents import financial_analyst, verifier, investment_advisor, risk_assessor
        from task import (
            analyze_financial_document,
            verification,
            investment_analysis,
            risk_assessment,
        )
        from database import SessionLocal
        from models import AnalysisResult
        
        # Update task status to running
        db = SessionLocal()
        try:
            analysis = db.query(AnalysisResult).filter(
                AnalysisResult.id == analysis_id
            ).first()
            
            if analysis:
                analysis.status = "processing"
                analysis.task_id = self.request.id
                db.commit()
        finally:
            db.close()
        
        # Update Celery task state
        self.update_state(state="PROGRESS", meta={"current": 20, "total": 100})
        
        # Run the financial analysis crew
        financial_crew = Crew(
            agents=[verifier, financial_analyst, investment_advisor, risk_assessor],
            tasks=[
                verification,
                analyze_financial_document,
                investment_analysis,
                risk_assessment,
            ],
            process=Process.sequential,
        )
        
        self.update_state(state="PROGRESS", meta={"current": 40, "total": 100})
        
        # Execute analysis
        result = financial_crew.kickoff(
            {"query": query, "file_path": file_path}
        )
        
        self.update_state(state="PROGRESS", meta={"current": 80, "total": 100})
        
        # Save results to database
        db = SessionLocal()
        try:
            analysis = db.query(AnalysisResult).filter(
                AnalysisResult.id == analysis_id
            ).first()
            
            if analysis:
                analysis.status = "completed"
                analysis.analysis = str(result)
                analysis.completed_at = datetime.utcnow()
                db.commit()
        finally:
            db.close()
        
        return {
            "status": "success",
            "analysis_id": analysis_id,
            "result": str(result),
        }
        
    except Exception as e:
        # Update task status to failed
        db = SessionLocal()
        try:
            analysis = db.query(AnalysisResult).filter(
                AnalysisResult.id == analysis_id
            ).first()
            
            if analysis:
                analysis.status = "failed"
                analysis.error_message = str(e)
                analysis.completed_at = datetime.utcnow()
                db.commit()
        finally:
            db.close()
        
        raise


@celery_app.task(name="cleanup_old_results")
def cleanup_old_results():
    """Cleanup old analysis results from database"""
    from datetime import timedelta
    from database import SessionLocal
    from models import AnalysisResult
    
    try:
        db = SessionLocal()
        try:
            # Delete results older than 30 days
            cutoff_date = datetime.utcnow() - timedelta(days=30)
            deleted_count = db.query(AnalysisResult).filter(
                AnalysisResult.created_at < cutoff_date
            ).delete()
            db.commit()
            
            return {
                "status": "success",
                "deleted_records": deleted_count,
            }
        finally:
            db.close()
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
        }


# Optional: Schedule periodic cleanup task
from celery.schedules import crontab

celery_app.conf.beat_schedule = {
    "cleanup-old-results": {
        "task": "cleanup_old_results",
        "schedule": crontab(hour=2, minute=0),  # Run at 2 AM daily
    },
}
