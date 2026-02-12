from fastapi import FastAPI

app = FastAPI(title="EduTech Risk Prediction API")

@app.get("/")
def root():
  return {"message": "EduTech Risk Prediction API"}

@app.get("/health")
def health():
  return {"status": "ok"}
