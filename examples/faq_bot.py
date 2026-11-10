"""A deliberately mediocre FAQ bot, so the eval has something to catch.

It pattern-matches a few questions and gets one of them wrong on purpose
(see evals/faq-dataset.json: the hours answer omits Sunday). Running
evalkit against it demonstrates a FAIL row with an actionable detail line.
"""

from __future__ import annotations

_RULES = [
    (("hour", "open", "close"), "We are open Monday to Saturday, 9am to 6pm."),
    (("refund", "return"), "Refunds are issued to the original payment method within 5 days."),
    (("ship", "deliver"), "Shipping is free on orders over $50 and takes 3-5 business days."),
    (("contact", "support", "help"), "Email support@example.com and we reply within a day."),
]


def answer(question: str) -> str:
    q = question.lower()
    for keywords, reply in _RULES:
        if any(k in q for k in keywords):
            return reply
    return "I don't know that one."
