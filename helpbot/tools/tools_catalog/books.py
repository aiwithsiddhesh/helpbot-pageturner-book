from helpbot.tools.engine.base import Tool
from helpbot.db import get_connection


class CheckBookAvailability(Tool):
    """Check the stock availability of a specific book by title."""
    properties = {
        "title": "The title of the book to check availability for.",
    }

    def run(self, title: str) -> dict:
        with get_connection() as conn:
            row = conn.execute("SELECT * FROM books WHERE title = ?", (title.lower().strip(),)).fetchone()
        if not row:
            return {"found": False, "title": title, "message": "This title is not in our catalogue."}
        data = dict(row)
        data["formats"] = data["formats"].split(",")
        return {"found": True, **data}


class GetRestockDate(Tool):
    """Get the expected restock date for a book that is currently out of stock. Only call this tool when check_book_availability returns out_of_stock."""
    properties = {
        "title": "The title of the out-of-stock book.",
    }

    def run(self, title: str) -> dict:
        with get_connection() as conn:
            row = conn.execute(
                "SELECT restock_date, restock_confidence FROM books WHERE title = ?",
                (title.lower().strip(),)
            ).fetchone()
        if not row or not row["restock_confidence"]:
            return {"found": False, "title": title, "message": "No restock information available for this title."}
        return {"found": True, "title": title, "restock_date": row["restock_date"], "confidence": row["restock_confidence"]}
