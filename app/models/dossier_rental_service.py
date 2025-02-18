from sqlalchemy import Table, Column, Integer, ForeignKey, Float, DateTime
from datetime import datetime
from ..database import Base

dossier_rental_services = Table(
    "dossier_rental_services",
    Base.metadata,
    Column("dossier_id", Integer, ForeignKey("dossiers.id")),
    Column("service_id", Integer, ForeignKey("rental_services.id")),
    Column("monthly_price", Float, nullable=False),
    Column("start_date", DateTime, nullable=False),
    Column("end_date", DateTime, nullable=False),
) 