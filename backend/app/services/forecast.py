from sqlalchemy.orm import Session

from .analytics import monthly_revenue


def forecast_next_month(db: Session) -> dict:
    history = monthly_revenue(db)
    if len(history) < 2:
        return {"history": history, "prediction": None, "method": "insufficient_data"}

    x = list(range(len(history)))
    y = [item["revenue"] for item in history]

    try:
        from sklearn.ensemble import RandomForestRegressor

        model = RandomForestRegressor(n_estimators=80, random_state=42)
        model.fit([[value] for value in x], y)
        prediction = float(model.predict([[len(history)]])[0])
        method = "scikit-learn RandomForestRegressor"
    except Exception:
        slope = (y[-1] - y[0]) / max(len(y) - 1, 1)
        prediction = y[-1] + slope
        method = "linear trend fallback"

    return {
        "history": history,
        "prediction": round(max(prediction, 0), 2),
        "method": method,
    }
