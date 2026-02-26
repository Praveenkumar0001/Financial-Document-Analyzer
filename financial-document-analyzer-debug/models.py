"""SQLAlchemy ORM models for Financial Document Analyzer"""

from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, Boolean, Integer, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.sqlite import JSON

Base = declarative_base()


class AnalysisResult(Base):
    """Model to store financial document analysis results"""
    
    __tablename__ = "analysis_results"
    
    id = Column(String(36), primary_key=True)
    file_name = Column(String(255), nullable=False)
    query = Column(Text, nullable=False)
    analysis = Column(Text, nullable=False)
    status = Column(String(20), default="pending")  # pending, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    task_id = Column(String(100), nullable=True)
    error_message = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<AnalysisResult(id={self.id}, file_name={self.file_name}, status={self.status})>"


class DocumentMetadata(Base):
    """Model to store document metadata"""
    
    __tablename__ = "document_metadata"
    
    id = Column(String(36), primary_key=True)
    document_id = Column(String(36), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=True)  # in bytes
    pages = Column(Integer, nullable=True)
    document_type = Column(String(50), nullable=True)  # financial_statement, annual_report, etc.
    is_verified = Column(Boolean, default=False)
    verified_at = Column(DateTime, nullable=True)
    upload_date = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<DocumentMetadata(id={self.id}, file_name={self.file_name})>"


class AnalysisCache(Base):
    """Model to cache analysis results for performance"""
    
    __tablename__ = "analysis_cache"
    
    id = Column(String(100), primary_key=True)
    query_hash = Column(String(64), nullable=False, unique=True)
    result = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    hit_count = Column(Integer, default=0)
    
    def __repr__(self):
        return f"<AnalysisCache(query_hash={self.query_hash})>"


class AuditLog(Base):
    """Model to track audit logs for compliance and monitoring"""
    
    __tablename__ = "audit_logs"
    
    id = Column(String(36), primary_key=True)
    action = Column(String(100), nullable=False)  # analysis_started, analysis_completed, etc.
    document_id = Column(String(36), nullable=True)
    user_ip = Column(String(20), nullable=True)
    status = Column(String(20), nullable=False)  # success, failure
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<AuditLog(action={self.action}, status={self.status}, timestamp={self.timestamp})>"
