"""
SQLAlchemy database models
"""
from sqlalchemy import Column, String, Float, DateTime, JSON, Integer, Index, Text
from sqlalchemy.sql import func
from api.core.database import Base

class CachedData(Base):
    """Model for cached economic data"""
    __tablename__ = "cached_data"
    
    id = Column(Integer, primary_key=True, index=True)
    cache_key = Column(String(255), unique=True, index=True, nullable=False)
    indicator_id = Column(String(100), index=True)
    country_code = Column(String(10), index=True)
    source = Column(String(50), index=True)
    data = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    expires_at = Column(DateTime(timezone=True), index=True)
    
    __table_args__ = (
        Index('idx_indicator_country', 'indicator_id', 'country_code'),
        Index('idx_cache_expires', 'cache_key', 'expires_at'),
    )

class APIRequestLog(Base):
    """Model for API request logging"""
    __tablename__ = "api_request_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    endpoint = Column(String(255), index=True)
    method = Column(String(10))
    ip_address = Column(String(45))
    user_agent = Column(Text)
    api_key = Column(String(255), index=True, nullable=True)
    status_code = Column(Integer)
    response_time = Column(Float)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    error_message = Column(Text, nullable=True)
    
    __table_args__ = (
        Index('idx_endpoint_timestamp', 'endpoint', 'timestamp'),
    )

class Indicator(Base):
    """Model for indicator metadata"""
    __tablename__ = "indicators"
    
    id = Column(Integer, primary_key=True, index=True)
    indicator_id = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    category = Column(String(50), index=True)
    description = Column(Text)
    unit = Column(String(50))
    frequency = Column(String(20))
    source = Column(String(50))
    metadata = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Country(Base):
    """Model for country information"""
    __tablename__ = "countries"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(10), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    region = Column(String(100))
    income_level = Column(String(50))
    population = Column(Integer)
    currency = Column(String(10))
    metadata = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

