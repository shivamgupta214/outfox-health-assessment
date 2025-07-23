from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.schema import UniqueConstraint


Base = declarative_base()

class HospitalData(Base):
    __tablename__ = "hospital_data"
    id = Column(Integer, primary_key=True, autoincrement=True)
    provider_id = Column(Integer, nullable=False)
    provider_name = Column(String)
    provider_city = Column(String)
    provider_state = Column(String)
    provider_zip_code = Column(String, index=True)  # Add index
    ms_drg_definition = Column(String, index=True)  # Add index
    total_discharges = Column(Integer)
    average_covered_charges = Column(Float)
    average_total_payments = Column(Float)
    average_medicare_payments = Column(Float)

    def __repr__(self):
        return f"<HospitalData(id={self.id}, provider_id={self.provider_id}, name={self.provider_name}, provider_city={self.provider_city}, provider_state={self.provider_state}, provider_zip_code={self.provider_zip_code}, ms_drg_definition={self.ms_drg_definition}, total_discharges={self.total_discharges}, average_covered_charges={self.average_covered_charges}, average_total_payments={self.average_total_payments}, average_medicare_payments={self.average_medicare_payments})>"


class StarRating(Base):
    __tablename__ = "star_rating"
    id = Column(Integer, primary_key=True, autoincrement=True)
    provider_id = Column(Integer, nullable=False)
    overall_rating = Column(Integer)

    __table_args__ = (UniqueConstraint('provider_id', name='uq_star_rating_provider_id'),)

    def __repr__(self):
        return f"<StarRating(id={self.id}, provider_id={self.provider_id}, overall_rating={self.overall_rating}, mortality_rating={self.mortality_rating}, safety_of_care_rating={self.safety_of_care_rating}, readmission_rating={self.readmission_rating}, patient_experience_rating={self.patient_experience_rating}, effective_care_rating={self.effective_care_rating})>"