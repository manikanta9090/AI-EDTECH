from datetime import datetime
import random
from app.database import SessionLocal, init_db
from app.models import Student, Course, Enrollment

def seed_db():
    init_db()
    db = SessionLocal()

    grades = ["A", "B", "C", "D", "E"]
    categories = ["Programming", "Data Science", "AI/ML", "Web Dev", "Cybersecurity"]
    course_names = ["Python", "Java", "SQL", "Machine Learning", "React"]

    for i in range(10):
        db.add(Student(name=f"Student {i+1}", grade=random.choice(grades)))

    for i in range(5):
        db.add(Course(name=course_names[i], category=categories[i]))

    for _ in range(20):
        db.add(Enrollment(
            student_id=random.randint(1, 10),
            course_id=random.randint(1, 5),
            enrolled_at=datetime(2024, random.randint(1, 12), random.randint(1, 28))
        ))

    db.commit()
    db.close()
    print("Database seeded successfully!")


if __name__ == "__main__":
    seed_db()