"""
Database configuration and ORM models for GCFB Operational Intelligence Dashboard.
"""

from sqlalchemy import (
    create_engine, Column, Integer, String, Float, Date, DateTime,
    ForeignKey, UniqueConstraint, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from typing import Optional
import os
from dotenv import load_dotenv

Base = declarative_base()


class PartnerSite(Base):
    """Partner site serving food to communities."""
    __tablename__ = 'partner_sites'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    address = Column(String(300), nullable=False)
    zip_code = Column(String(10), nullable=False, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    program_type = Column(String(50), nullable=False, index=True)
    capacity_per_day = Column(Integer, nullable=False)
    operating_days = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    
    distributions = relationship("HistoricalDistribution", back_populates="site")
    
    def __repr__(self):
        return f"<PartnerSite(id={self.id}, name='{self.name}', zip='{self.zip_code}', type='{self.program_type}')>"


class HistoricalDistribution(Base):
    """Historical distribution records showing past demand patterns."""
    __tablename__ = 'historical_distribution'
    __table_args__ = (
        UniqueConstraint('site_id', 'date', name='unique_site_date'),
        Index('idx_historical_date', 'date'),
        Index('idx_historical_site', 'site_id'),
        Index('idx_historical_site_date', 'site_id', 'date'),
    )
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    site_id = Column(Integer, ForeignKey('partner_sites.id'), nullable=False)
    date = Column(Date, nullable=False)
    headcount = Column(Integer, nullable=False)
    program_type = Column(String(50), nullable=False)
    temperature_f = Column(Float, nullable=True)
    precipitation_inches = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    
    site = relationship("PartnerSite", back_populates="distributions")
    
    def __repr__(self):
        return f"<HistoricalDistribution(site_id={self.site_id}, date={self.date}, headcount={self.headcount})>"


class WarehouseInventory(Base):
    """Warehouse inventory items with expiration dates."""
    __tablename__ = 'warehouse_inventory'
    __table_args__ = (
        Index('idx_inventory_expiration', 'expiration_date'),
        Index('idx_inventory_category', 'category'),
    )
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    item_name = Column(String(200), nullable=False)
    category = Column(String(50), nullable=False)
    quantity = Column(Float, nullable=False)
    unit = Column(String(20), nullable=False)
    expiration_date = Column(Date, nullable=False)
    received_date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    
    def __repr__(self):
        return f"<WarehouseInventory(id={self.id}, item='{self.item_name}', expires={self.expiration_date})>"


class TruckFleet(Base):
    """Truck fleet information."""
    __tablename__ = 'truck_fleet'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    truck_number = Column(String(20), nullable=False, unique=True)
    capacity_lbs = Column(Integer, nullable=False)
    status = Column(String(20), nullable=False, default='active')
    created_at = Column(DateTime, default=datetime.now)
    
    def __repr__(self):
        return f"<TruckFleet(id={self.id}, truck='{self.truck_number}', capacity={self.capacity_lbs})>"


class VolunteerAvailability(Base):
    """Daily volunteer availability counts."""
    __tablename__ = 'volunteer_availability'
    __table_args__ = (
        Index('idx_volunteer_date', 'date'),
    )
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False, unique=True)
    volunteer_count = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    
    def __repr__(self):
        return f"<VolunteerAvailability(date={self.date}, count={self.volunteer_count})>"


def get_engine(database_url: Optional[str] = None):
    """
    Create and return SQLAlchemy engine.
    
    Args:
        database_url: Optional database URL. If not provided, loads from environment.
        
    Returns:
        SQLAlchemy engine instance
    """
    if database_url is None:
        load_dotenv()
        database_url = os.getenv('DATABASE_URL')
        
        if not database_url:
            # Use in-memory SQLite for demo/deployment environments
            database_url = "sqlite:///:memory:"
            print("Using in-memory SQLite database (data will be lost on restart)")
    
    engine = create_engine(database_url, echo=False)
    return engine


def init_db(engine):
    """
    Initialize database by dropping and recreating all tables.
    
    WARNING: This will delete all existing data!
    
    Args:
        engine: SQLAlchemy engine instance
    """
    print("Dropping all existing tables...")
    Base.metadata.drop_all(bind=engine)
    
    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)
    
    print("Database initialized successfully!")


def get_session(engine):
    """
    Create and return a new database session.
    
    Args:
        engine: SQLAlchemy engine instance
        
    Returns:
        SQLAlchemy session instance
    """
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()


def get_db():
    """
    Dependency for FastAPI routes to get database session.
    
    Yields:
        Database session
    """
    load_dotenv()
    database_url = os.getenv('DATABASE_URL')
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
