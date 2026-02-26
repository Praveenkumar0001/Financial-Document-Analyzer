from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import uuid
from datetime import datetime

from crewai import Crew, Process
from agents import financial_analyst, verifier, investment_advisor, risk_assessor
from task import analyze_financial_document, verification, investment_analysis, risk_assessment

# Optional: Database and async dependencies
try:
    from database import init_db, SessionLocal
    from models import AnalysisResult, DocumentMetadata, AuditLog
    from queue_worker import celery_app, analyze_document_task
    FEATURES_ENABLED = {
        "database": True,
        "async": True,
    }
except ImportError:
    FEATURES_ENABLED = {
        "database": False,
        "async": False,
    }

app = FastAPI(
    title="Financial Document Analyzer",
    description="Advanced financial document analysis using multi-agent AI orchestration"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
if FEATURES_ENABLED["database"]:
    try:
        init_db()
    except Exception as e:
        print(f"⚠️ Database initialization skipped: {str(e)}")


def run_crew(query: str, file_path: str="data/sample.pdf"):
    """Run the financial analysis crew with all agents"""
    financial_crew = Crew(
        agents=[verifier, financial_analyst, investment_advisor, risk_assessor],
        tasks=[verification, analyze_financial_document, investment_analysis, risk_assessment],
        process=Process.sequential,
    )
    
    result = financial_crew.kickoff({"query": query, "file_path": file_path})
    return result


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Financial Document Analyzer API is running",
        "version": "2.0",
        "features": FEATURES_ENABLED,
    }


@app.get("/health")
async def health_check():
    """Extended health check with feature status"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "database": FEATURES_ENABLED["database"],
        "async_processing": FEATURES_ENABLED["async"],
    }


@app.post("/analyze")
async def analyze_document_sync(
    file: UploadFile = File(...),
    query: str = Form(default="Analyze this financial document for investment insights")
):
    """
    Synchronous document analysis endpoint (Legacy/Backward compatible)
    Process completes immediately and returns results
    """
    
    file_id = str(uuid.uuid4())
    file_path = f"data/financial_document_{file_id}.pdf"
    
    try:
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)
        
        # Save uploaded file
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Validate query
        if not query or query == "":
            query = "Analyze this financial document for investment insights"
        
        # Log to database if enabled
        if FEATURES_ENABLED["database"]:
            try:
                db = SessionLocal()
                audit_log = AuditLog(
                    id=str(uuid.uuid4()),
                    action="analysis_started",
                    document_id=file_id,
                    status="success",
                    details=f"Synchronous analysis started for {file.filename}"
                )
                db.add(audit_log)
                db.commit()
                db.close()
            except Exception as e:
                print(f"⚠️ Audit logging failed: {str(e)}")
        
        # Process the financial document with all analysts
        response = run_crew(query=query.strip(), file_path=file_path)
        
        return {
            "status": "success",
            "type": "synchronous",
            "query": query,
            "analysis": str(response),
            "file_processed": file.filename,
            "analysis_id": file_id,
        }
        
    except Exception as e:
        # Log error to database if enabled
        if FEATURES_ENABLED["database"]:
            try:
                db = SessionLocal()
                audit_log = AuditLog(
                    id=str(uuid.uuid4()),
                    action="analysis_failed",
                    document_id=file_id,
                    status="failure",
                    details=str(e)
                )
                db.add(audit_log)
                db.commit()
                db.close()
            except:
                pass
        
        raise HTTPException(status_code=500, detail=f"Error processing financial document: {str(e)}")
    
    finally:
        # Clean up uploaded file
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass  # Ignore cleanup errors


# ============= BONUS FEATURES: Async Processing & Database =============

if FEATURES_ENABLED["async"]:
    
    @app.post("/analyze/async")
    async def analyze_document_async(
        file: UploadFile = File(...),
        query: str = Form(default="Analyze this financial document for investment insights")
    ):
        """
        Asynchronous document analysis endpoint (BONUS FEATURE)
        Returns immediately with a task ID for tracking progress
        Use /status/{analysis_id} to check progress
        """
        
        analysis_id = str(uuid.uuid4())
        file_id = str(uuid.uuid4())
        file_path = f"data/financial_document_{file_id}.pdf"
        
        try:
            # Ensure data directory exists
            os.makedirs("data", exist_ok=True)
            
            # Save uploaded file
            with open(file_path, "wb") as f:
                content = await file.read()
                f.write(content)
            
            # Validate query
            if not query or query == "":
                query = "Analyze this financial document for investment insights"
            
            # Store in database
            db = SessionLocal()
            
            # Save document metadata
            doc_metadata = DocumentMetadata(
                id=file_id,
                document_id=analysis_id,
                file_name=file.filename,
                upload_date=datetime.utcnow(),
            )
            db.add(doc_metadata)
            
            # Create analysis record
            analysis_result = AnalysisResult(
                id=analysis_id,
                file_name=file.filename,
                query=query,
                analysis="",
                status="pending",
                created_at=datetime.utcnow(),
            )
            db.add(analysis_result)
            
            # Log audit
            audit_log = AuditLog(
                id=str(uuid.uuid4()),
                action="analysis_queued",
                document_id=file_id,
                status="success",
                details=f"Async analysis queued for {file.filename}"
            )
            db.add(audit_log)
            db.commit()
            db.close()
            
            # Queue the async task
            task = analyze_document_task.delay(
                file_path=file_path,
                query=query.strip(),
                analysis_id=analysis_id
            )
            
            return {
                "status": "queued",
                "analysis_id": analysis_id,
                "task_id": task.id,
                "message": "Analysis queued for processing. Use /status/{analysis_id} to check progress",
                "file_processed": file.filename,
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error queuing analysis: {str(e)}")
    
    
    @app.get("/status/{analysis_id}")
    async def get_analysis_status(analysis_id: str):
        """
        Get the status of an async analysis (BONUS FEATURE)
        Returns current progress and results when available
        """
        
        try:
            db = SessionLocal()
            analysis = db.query(AnalysisResult).filter(
                AnalysisResult.id == analysis_id
            ).first()
            db.close()
            
            if not analysis:
                raise HTTPException(status_code=404, detail="Analysis not found")
            
            response = {
                "analysis_id": analysis_id,
                "status": analysis.status,
                "query": analysis.query,
                "file_name": analysis.file_name,
                "created_at": analysis.created_at.isoformat() if analysis.created_at else None,
                "updated_at": analysis.updated_at.isoformat() if analysis.updated_at else None,
                "completed_at": analysis.completed_at.isoformat() if analysis.completed_at else None,
            }
            
            if analysis.status == "completed":
                response["analysis"] = analysis.analysis
                response["message"] = "Analysis completed successfully"
            elif analysis.status == "failed":
                response["error"] = analysis.error_message
                response["message"] = "Analysis failed"
            elif analysis.status == "processing":
                response["message"] = "Analysis is being processed"
            elif analysis.status == "pending":
                response["message"] = "Analysis is queued for processing"
            
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving status: {str(e)}")
    
    
    @app.get("/results/{analysis_id}")
    async def get_analysis_results(analysis_id: str):
        """
        Get completed analysis results (BONUS FEATURE)
        Returns full analysis once completed
        """
        
        try:
            db = SessionLocal()
            analysis = db.query(AnalysisResult).filter(
                AnalysisResult.id == analysis_id
            ).first()
            db.close()
            
            if not analysis:
                raise HTTPException(status_code=404, detail="Analysis not found")
            
            if analysis.status != "completed":
                raise HTTPException(
                    status_code=202,
                    detail=f"Analysis not ready. Current status: {analysis.status}"
                )
            
            return {
                "analysis_id": analysis_id,
                "status": "completed",
                "query": analysis.query,
                "file_name": analysis.file_name,
                "analysis": analysis.analysis,
                "completed_at": analysis.completed_at.isoformat() if analysis.completed_at else None,
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving results: {str(e)}")
    
    
    @app.get("/history")
    async def get_analysis_history(limit: int = 10):
        """
        Get recent analysis history (BONUS FEATURE)
        Returns list of recent analyses
        """
        
        try:
            db = SessionLocal()
            analyses = db.query(AnalysisResult).order_by(
                AnalysisResult.created_at.desc()
            ).limit(limit).all()
            db.close()
            
            return {
                "count": len(analyses),
                "analyses": [
                    {
                        "analysis_id": a.id,
                        "file_name": a.file_name,
                        "query": a.query[:100] + "..." if len(a.query) > 100 else a.query,
                        "status": a.status,
                        "created_at": a.created_at.isoformat() if a.created_at else None,
                        "completed_at": a.completed_at.isoformat() if a.completed_at else None,
                    }
                    for a in analyses
                ]
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving history: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("Financial Document Analyzer API")
    print("=" * 60)
    print("Starting server on 0.0.0.0:8000...")
    print(f"✅ Features enabled: Database={FEATURES_ENABLED['database']}, Async={FEATURES_ENABLED['async']}")
    print("\n📚 Endpoints:")
    print("  GET  /              - Health check")
    print("  POST /analyze       - Synchronous analysis")
    if FEATURES_ENABLED["async"]:
        print("  POST /analyze/async - Asynchronous analysis (BONUS)")
        print("  GET  /status/{id}   - Check analysis status (BONUS)")
        print("  GET  /results/{id}  - Get analysis results (BONUS)")
        print("  GET  /history       - Analysis history (BONUS)")
    print("\n📖 API documentation: http://localhost:8000/docs")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=8000)