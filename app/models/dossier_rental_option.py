from sqlalchemy import Column, Integer, ForeignKey, Table
from ..database import Base

dossier_rental_options = Table(
    "dossier_rental_options",
    Base.metadata,
    Column("dossier_id", Integer, ForeignKey("dossiers.id")),
    Column("rental_option_id", Integer, ForeignKey("rental_options.id")),
) 