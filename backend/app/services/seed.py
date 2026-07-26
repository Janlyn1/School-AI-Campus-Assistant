from datetime import date

from sqlalchemy.orm import Session

from ..models import Customer, Employee, InventoryItem, KnowledgeDocument, Sale


def seed_database(db: Session) -> None:
    if db.query(Sale).first():
        return

    sales = [
        Sale(date=date(2026, 1, 12), product="Embedded Systems Lab", category="Computer Engineering", quantity=28, amount=87, customer_segment="3rd Year"),
        Sale(date=date(2026, 2, 18), product="Embedded Systems Lab", category="Computer Engineering", quantity=31, amount=89, customer_segment="3rd Year"),
        Sale(date=date(2026, 3, 20), product="Data Structures Project", category="Computer Engineering", quantity=34, amount=84, customer_segment="2nd Year"),
        Sale(date=date(2026, 4, 14), product="Data Structures Project", category="Computer Engineering", quantity=36, amount=86, customer_segment="2nd Year"),
        Sale(date=date(2026, 5, 6), product="AI Chatbot Prototype", category="Capstone", quantity=12, amount=91, customer_segment="4th Year"),
        Sale(date=date(2026, 6, 9), product="AI Chatbot Prototype", category="Capstone", quantity=15, amount=93, customer_segment="4th Year"),
        Sale(date=date(2026, 6, 22), product="Network Security Lab", category="Computer Engineering", quantity=24, amount=82, customer_segment="3rd Year"),
        Sale(date=date(2026, 7, 5), product="Network Security Lab", category="Computer Engineering", quantity=26, amount=85, customer_segment="3rd Year"),
        Sale(date=date(2026, 7, 12), product="Capstone Defense Prep", category="Capstone", quantity=18, amount=90, customer_segment="4th Year"),
    ]

    inventory = [
        InventoryItem(sku="LAB-100", product="Arduino Uno Kit", category="Embedded Systems", stock_remaining=9, reorder_level=12, supplier="Engineering Lab"),
        InventoryItem(sku="LAB-240", product="Breadboard Set", category="Electronics", stock_remaining=7, reorder_level=10, supplier="Engineering Lab"),
        InventoryItem(sku="LAB-330", product="Raspberry Pi Kit", category="IoT", stock_remaining=18, reorder_level=8, supplier="Engineering Lab"),
        InventoryItem(sku="LAB-410", product="Jumper Wire Pack", category="Electronics", stock_remaining=5, reorder_level=15, supplier="Engineering Lab"),
        InventoryItem(sku="LAB-150", product="Multimeter", category="Electronics", stock_remaining=11, reorder_level=10, supplier="Engineering Lab"),
    ]

    employees = [
        Employee(name="Mia Santos", department="Computer Engineering", performance_score=94, open_tasks=4, manager="Engr. Lee"),
        Employee(name="Jacob Reed", department="Computer Engineering", performance_score=68, open_tasks=13, manager="Engr. Kim"),
        Employee(name="Ava Chen", department="Capstone", performance_score=91, open_tasks=6, manager="Dr. Patel"),
        Employee(name="Leo Martin", department="Computer Engineering", performance_score=72, open_tasks=15, manager="Engr. Lee"),
        Employee(name="Nina Patel", department="Capstone", performance_score=86, open_tasks=8, manager="Dr. Kim"),
    ]

    customers = [
        Customer(name="Miguel Cruz", segment="4th Year", lifetime_value=91, churn_risk=0.18, region="Capstone A"),
        Customer(name="Angel Reyes", segment="3rd Year", lifetime_value=88, churn_risk=0.11, region="Embedded Lab"),
        Customer(name="Rafa Santos", segment="2nd Year", lifetime_value=72, churn_risk=0.62, region="Data Structures"),
        Customer(name="Celine Tan", segment="4th Year", lifetime_value=85, churn_risk=0.27, region="Capstone B"),
        Customer(name="Noah Garcia", segment="3rd Year", lifetime_value=74, churn_risk=0.54, region="Networking Lab"),
    ]

    docs = [
        KnowledgeDocument(
            title="Capstone Progress Review",
            source_type="PDF",
            content=(
                "Capstone progress improved after adviser check-ins and prototype review sessions. "
                "Some groups still need help with documentation, testing, and lab equipment availability. "
                "Faculty recommends monitoring delayed teams and prioritizing access to embedded systems kits."
            ),
        ),
        KnowledgeDocument(
            title="Student Support Playbook",
            source_type="DOCX",
            content=(
                "Students with risk above 0.50 should receive an adviser review within seven days. "
                "The review should include attendance, pending tasks, lab access issues, and academic support needs."
            ),
        ),
        KnowledgeDocument(
            title="Lab Inventory Policy",
            source_type="DOCX",
            content=(
                "Lab supplies below reorder level require a lab assistant notification and weekly faculty visibility. "
                "Embedded systems and electronics materials should be prioritized because they affect project timelines."
            ),
        ),
    ]

    db.add_all([*sales, *inventory, *employees, *customers, *docs])
    db.commit()
