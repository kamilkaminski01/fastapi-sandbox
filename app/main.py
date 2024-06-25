from typing import Annotated, List

import models
from database import engine, get_db
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

db_dependency = Annotated[Session, Depends(get_db)]


class ChoiceBase(BaseModel):
    choice_text: str
    is_correct: bool


class QuestionBase(BaseModel):
    question_text: str
    choices: List[ChoiceBase]


@app.get("/questions/{question_id}")
async def read_question(question_id: int, db: db_dependency):
    result = (
        db.query(models.Questions).filter(models.Questions.id == question_id).first()
    )
    if not result:
        raise HTTPException(status_code=404, detail="Question not found")
    return result


@app.post("/questions/")
async def create_question(question: QuestionBase, db: db_dependency):
    db_question = models.Questions(question_text=question.question_text)
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    for choice in question.choices:
        db_choice = models.Choices(
            choice_text=choice.choice_text,
            is_correct=choice.is_correct,
            question_id=db_question.id,
        )
        db.add(db_choice)
    db.commit()


@app.get("/choices/{question_id}")
async def read_choices(question_id: int, db: db_dependency):
    result = (
        db.query(models.Choices).filter(models.Choices.question_id == question_id).all()
    )
    if not result:
        raise HTTPException(status_code=404, detail="Choices not found")
    return result
