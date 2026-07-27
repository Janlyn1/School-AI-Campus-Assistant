from app.services.intent_classifier import classifier_evaluation, classify_inquiry


def test_classifier_evaluation_is_reproducible():
    evaluation = classifier_evaluation()

    assert evaluation["dataset_size"] == 294
    assert evaluation["train_size"] + evaluation["test_size"] == evaluation["dataset_size"]
    assert 0 <= evaluation["accuracy"] <= 1
    assert len(evaluation["confusion_matrix"]) == len(evaluation["labels"])


def test_classifier_routes_library_question():
    prediction = classify_inquiry("What time does the library open?")

    assert prediction["label"] == "Library"
    assert prediction["model"] == "TF-IDF + Logistic Regression"
