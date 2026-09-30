from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# Import our custom agent function
from agent import run_shopping_agent

app = FastAPI(title="Shopping Agent API")

# --- DATABASE SETUP (SQLite) ---
Base = declarative_base()
engine = create_engine('sqlite:///shopping_history.db', connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

class SearchHistory(Base):
    __tablename__ = "history"
    id = Column(Integer, primary_key=True, index=True)
    query = Column(String, index=True)
    recommendation = Column(Text)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- API ENDPOINTS ---
class ShoppingRequest(BaseModel):
    query: str

@app.post("/search")
def search_products(request: ShoppingRequest, db: Session = Depends(get_db)):
    # 1. Trigger the agent logic
    response_text = run_shopping_agent(request.query)
    
    # 2. Save the query and response to the SQLite database
    new_record = SearchHistory(query=request.query, recommendation=response_text)
    db.add(new_record)
    db.commit()
    
    # 3. Return to the frontend
    return {"response": response_text}

@app.get("/history")
def get_history(db: Session = Depends(get_db)):
    records = db.query(SearchHistory).order_by(SearchHistory.id.desc()).limit(5).all()
    return [{"query": r.query, "recommendation": r.recommendation} for r in records]