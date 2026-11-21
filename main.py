from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
from database import create_connection

app = FastAPI(
    title="Banking Survey and Analytics API"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500"
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {
        "message": "Welcome to Banking Survey and Analytics!"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


@app.get("/survey")
def get_survey():
    return {
        "title": "Banking Customer Satisfaction Survey",
        "questions": [
            "How satisfied are you with your bank?",
            "How easy is it to use your bank's mobile app?",
            "How would you rate the customer service?",
            "Are banking transactions completed quickly?",
            "Would you recommend your bank to others?"
        ]
    }

@app.get("/customer-profile")
def get_customer_profile():
    return {
        "customer_id": 101,
        "age_group": "21-30",
        "account_type": "Savings",
        "digital_banking_user": True,
        "preferred_channel": "Mobile App",
        "satisfaction_level": "Satisfied"
    }

from pydantic import BaseModel, Field
from typing import List

class SurveyResponse(BaseModel):
    customer_id: int = Field(gt=0)
    answers: List[str]




@app.post("/submit-survey")
def submit_survey(response: SurveyResponse):
    connection = create_connection()
    cursor = connection.cursor()

    answers_json = json.dumps(response.answers)

    cursor.execute(
        "INSERT INTO survey_responses (customer_id, answers) VALUES (?, ?)",
        (response.customer_id, answers_json)
    )

    connection.commit()
    saved_id = cursor.lastrowid
    connection.close()

    return {
        "message": "Survey response saved successfully!",
        "response_id": saved_id,
        "customer_id": response.customer_id,
        "answers_received": len(response.answers),
        "answers": response.answers
    }


@app.get("/analytics")
def get_analytics():
    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT COUNT(DISTINCT customer_id)
        FROM survey_responses
    """)
    total_customers = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM survey_responses
    """)
    total_responses = cursor.fetchone()[0]

    cursor.execute("""
        SELECT answers
        FROM survey_responses
    """)
    all_answers = cursor.fetchall()

    very_satisfied = 0
    satisfied = 0
    neutral = 0
    dissatisfied = 0
    very_dissatisfied = 0

    for row in all_answers:
        answers = json.loads(row[0])

        if answers:
            answer = answers[0].strip().lower()

            if answer == "very satisfied":
                very_satisfied += 1
            elif answer == "satisfied":
                satisfied += 1
            elif answer == "neutral":
                neutral += 1
            elif answer == "dissatisfied":
                dissatisfied += 1
            elif answer == "very dissatisfied":
                very_dissatisfied += 1

    total_rated = (
        very_satisfied + satisfied + neutral
        + dissatisfied + very_dissatisfied
    )

    satisfaction_percentage = 0

    if total_rated > 0:
        satisfaction_percentage = round(
            (very_satisfied + satisfied) / total_rated * 100, 2
        )

    connection.close()

    return {
        "total_customers": total_customers,
        "total_responses": total_responses,
        "very_satisfied": very_satisfied,
        "satisfied": satisfied,
        "neutral": neutral,
        "dissatisfied": dissatisfied,
        "very_dissatisfied": very_dissatisfied,
        "satisfaction_percentage": satisfaction_percentage
    }