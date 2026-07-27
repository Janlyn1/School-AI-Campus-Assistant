from functools import lru_cache


TRAINING_EXAMPLES = {
    "Registrar": [
        "How do I enroll for the next semester?",
        "I need a copy of my transcript.",
        "What are the graduation requirements?",
        "Can I change my enrolled subjects?",
        "Where can I view my grades?",
        "Paano mag enroll ngayong semester?",
        "Ilang units ang kailangan for graduation?",
        "Please submit my enrollment request.",
        "My prerequisite subject is not showing.",
        "When is the registration schedule?",
    ],
    "Finance": [
        "How much is my tuition balance?",
        "Where can I pay my school fees?",
        "My payment is not yet posted.",
        "Can I request an installment plan?",
        "How do I get my assessment form?",
        "Magkano ang tuition ko?",
        "Saan pwede magbayad ng balance?",
        "I need an official receipt.",
        "What are the laboratory fees?",
        "Can Finance check my payment?",
    ],
    "Scholarship": [
        "What scholarships are available?",
        "How can I apply for financial assistance?",
        "What grade is required for a merit scholarship?",
        "When is the scholarship application deadline?",
        "Do I qualify for academic scholarship?",
        "May scholarship ba para sa engineering?",
        "Ano ang requirements sa scholarship?",
        "I need the scholarship application form.",
        "Can working students apply for aid?",
        "Where do I submit proof of income?",
    ],
    "Library": [
        "What time does the library open?",
        "How many books can I borrow?",
        "Can I access online journals?",
        "I need research materials for my thesis.",
        "How do I renew a borrowed book?",
        "Bukas ba ang library sa Saturday?",
        "Paano humiram ng libro?",
        "Where is the library catalog?",
        "What is the overdue book policy?",
        "Can I reserve a study room?",
    ],
    "IT Support": [
        "How do I reset my WiFi password?",
        "My campus email is not working.",
        "I cannot sign in to the student portal.",
        "Where is the IT help desk?",
        "My school account is locked.",
        "Hindi gumagana ang campus WiFi.",
        "Paano mag reset ng password?",
        "I did not receive a verification email.",
        "The learning system is unavailable.",
        "Help me recover my campus account.",
    ],
    "Guidance": [
        "I need confidential counseling.",
        "Can someone help me with career planning?",
        "I feel stressed about my classes.",
        "Where can I get internship advice?",
        "Can Guidance review my resume?",
        "Kailangan ko ng counseling.",
        "Saan pwede humingi ng career advice?",
        "I want to schedule a guidance appointment.",
        "Can I practice for a job interview?",
        "I need academic coaching.",
    ],
    "Laboratory": [
        "I want to borrow an Arduino kit.",
        "Is the Raspberry Pi available?",
        "Borrow two breadboard sets.",
        "What lab equipment is in stock?",
        "I need a multimeter for our project.",
        "Pwede humiram ng jumper wires?",
        "May stock ba ng Arduino?",
        "Return the borrowed equipment.",
        "Which laboratory supplies are low?",
        "Request an embedded systems kit.",
    ],
}

TOPIC_AUGMENTATION = {
    "Registrar": ["enrollment schedule", "subject registration", "official transcript", "graduation clearance", "course units", "student grades", "prerequisite approval", "change of subjects"],
    "Finance": ["tuition balance", "school payment", "official receipt", "installment plan", "laboratory fee", "payment posting", "assessment amount", "finance hold"],
    "Scholarship": ["merit scholarship", "financial assistance", "scholarship deadline", "proof of income", "academic scholarship", "scholarship application", "grade requirement", "student grant"],
    "Library": ["library hours", "book borrowing", "online journals", "study room", "library catalog", "book renewal", "overdue policy", "research materials"],
    "IT Support": ["WiFi password", "campus email", "account recovery", "student portal login", "verification email", "IT help desk", "locked account", "learning system"],
    "Guidance": ["confidential counseling", "career planning", "academic stress", "internship advice", "resume review", "mock interview", "guidance appointment", "academic coaching"],
    "Laboratory": ["Arduino borrowing", "Raspberry Pi stock", "breadboard request", "lab inventory", "multimeter availability", "equipment return", "jumper wires", "embedded systems kit"],
}

for augmentation_label, topics in TOPIC_AUGMENTATION.items():
    for topic in topics:
        TRAINING_EXAMPLES[augmentation_label].extend(
            [
                f"I need help with {topic}.",
                f"Can you explain the process for {topic}?",
                f"Where can I request {topic}?",
                f"Paano ang {topic}?",
            ]
        )


@lru_cache(maxsize=1)
def get_classifier_bundle() -> dict:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import accuracy_score, confusion_matrix, precision_recall_fscore_support
    from sklearn.model_selection import train_test_split
    from sklearn.pipeline import Pipeline

    texts = []
    labels = []
    for label, examples in TRAINING_EXAMPLES.items():
        texts.extend(examples)
        labels.extend([label] * len(examples))

    x_train, x_test, y_train, y_test = train_test_split(
        texts,
        labels,
        test_size=0.3,
        random_state=42,
        stratify=labels,
    )
    pipeline = Pipeline(
        [
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), lowercase=True, strip_accents="unicode")),
            ("classifier", LogisticRegression(max_iter=1000, random_state=42)),
        ]
    )
    pipeline.fit(x_train, y_train)
    predictions = pipeline.predict(x_test)
    ordered_labels = sorted(TRAINING_EXAMPLES)
    precision, recall, f1, _ = precision_recall_fscore_support(
        y_test,
        predictions,
        labels=ordered_labels,
        average="macro",
        zero_division=0,
    )
    evaluation = {
        "model": "TF-IDF + Logistic Regression",
        "dataset_size": len(texts),
        "train_size": len(x_train),
        "test_size": len(x_test),
        "labels": ordered_labels,
        "accuracy": round(float(accuracy_score(y_test, predictions)), 3),
        "macro_precision": round(float(precision), 3),
        "macro_recall": round(float(recall), 3),
        "macro_f1": round(float(f1), 3),
        "confusion_matrix": confusion_matrix(y_test, predictions, labels=ordered_labels).tolist(),
        "split": "70% train / 30% test, stratified, random_state=42",
    }
    # Keep held-out metrics honest, then refit the deployable model on all labeled examples.
    pipeline.fit(texts, labels)
    return {"pipeline": pipeline, "evaluation": evaluation}


def classify_inquiry(message: str) -> dict:
    bundle = get_classifier_bundle()
    pipeline = bundle["pipeline"]
    probabilities = pipeline.predict_proba([message])[0]
    best_index = int(probabilities.argmax())
    label = str(pipeline.classes_[best_index])
    probability = float(probabilities[best_index])
    certainty = "High" if probability >= 0.55 else "Medium" if probability >= 0.35 else "Low"
    return {
        "label": label,
        "certainty": certainty,
        "model": bundle["evaluation"]["model"],
    }


def classifier_evaluation() -> dict:
    return get_classifier_bundle()["evaluation"]
