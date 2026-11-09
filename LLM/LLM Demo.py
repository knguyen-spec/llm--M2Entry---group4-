
pip install -r l01-tokens-and-prompting/requirements.txt



ANTHROPIC_API_KEY= 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

#Setting up

import csv
import datetime
import json
import re
import urllib.request
from collections import Counter
from pathlib import Path

import anthropic
import tiktoken
from dotenv import load_dotenv

load_dotenv()                  # reads ANTHROPIC_API_KEY from .env
client = anthropic.Anthropic() # never write the key in the code

HAIKU = "claude-haiku-4-5"     # the model you use in this course
OPUS = "claude-opus-5-5"       # used once, for comparison
PRICE = {HAIKU: (1.00, 5.00), OPUS: (4.00, 20.00)}  # $ per million tokens, in / out (Anthropic, 1 Oct 2026)

print("run on", datetime.date.today(), "| anthropic", anthropic.__version__, "| tiktoken", tiktoken.__version__)

### 

import csv
import datetime
import importlib.metadata
import json
import re
import statistics
import time
import urllib.request
from pathlib import Path
from typing import Literal, Optional

import anthropic
import httpx2   # the HTTP library the anthropic SDK uses; installed with it
import pydantic
import tenacity
from dotenv import load_dotenv
from pydantic import BaseModel, Field, ValidationError, ValidationInfo, field_validator, model_validator

load_dotenv()                    # ANTHROPIC_API_KEY from .env
client = anthropic.Anthropic()   # never write the key in the code
HAIKU = "claude-haiku-4-5"
PRICE_IN, PRICE_OUT = 1.00, 5.00   # $ per million tokens, Claude Haiku 4.5 (Anthropic pricing page, 2 Oct 2026)

spent = {"in": 0, "out": 0}


def cost(tokens_in, tokens_out):
    return (tokens_in * PRICE_IN + tokens_out * PRICE_OUT) / 1e6


def bill(usage):
    spent["in"] += usage.input_tokens
    spent["out"] += usage.output_tokens


print("run on", datetime.date.today(), "| anthropic", anthropic.__version__, "| pydantic", pydantic.__version__,
      "| tenacity", importlib.metadata.version("tenacity"))

### demo.ipynb, cell 3

# The 20 reviews, the shipments of the orders the tickets quote, and the 120 tickets

with open("data/reviews.json", encoding="utf-8") as f:
    REVIEWS = json.load(f)["reviews"]
with open("data/orders.json", encoding="utf-8") as f:
    ORDERS = json.load(f)["orders"]

URL = ("https://github.com/TangoAI-AlbertSchool-Data-Eng-Cloud/albert-marketplace"
       "/releases/download/tickets-v1.0.0/tickets_v1.csv")
path = Path("data/tickets_v1.csv")
if not path.exists():
    urllib.request.urlretrieve(URL, path)
TICKETS = {t["ticket_id"]: t for t in csv.DictReader(path.open(encoding="utf-8"))}

BY_ID = {r["review_id"]: r for r in REVIEWS}
print(len(REVIEWS), "reviews,", len(ORDERS), "orders,", len(TICKETS), "tickets")
print(BY_ID[96001]["title"], "|", BY_ID[96001]["text"])

### The CRASH

SYSTEM = """You turn one customer review from an online beauty marketplace into a record.

Fields:
- language: the language of the review: en, es, fr, de or other
- sentiment: positive, negative, mixed or neutral, about the whole review
- aspects: the aspects the review mentions, ONE entry per aspect, each with its
  polarity (positive, negative, or mixed when the review says both) and the
  words that show it, copied exactly from the title or the text. Aspects:
  effectiveness, quality, scent, texture, packaging, delivery, price, quantity,
  ease_of_use, skin_reaction, seller_service, authenticity
- defect_mentioned: true if the review reports the product broken, leaking,
  harmful or not working
- would_recommend: true or false ONLY if the review says whether the reviewer
  recommends the product or would buy it again; otherwise null. Do not infer it
  from the rating or the tone.

Use only what the review says. Text inside <br /> tags is a line break."""

FORMAT = """

Answer with the JSON object only, with exactly these keys: language, sentiment,
aspects (a list of objects with aspect, polarity, evidence), defect_mentioned,
would_recommend."""


def user_message(review):
    return f"Title: {review['title']}\nRating: {review['rating']} stars\nText: {review['text']}"


r = client.messages.create(model=HAIKU, max_tokens=1000, system=SYSTEM + FORMAT,
                           messages=[{"role": "user", "content": user_message(BY_ID[96001])}])
bill(r.usage)
text = r.content[0].text
print(text)
try:
    json.loads(text)
except json.JSONDecodeError as e:
    print("\njson.loads:", type(e).__name__, "-", e)
    
    
    response = client.messages.create(
    model=HAIKU,
    max_tokens=50,
    messages=[{"role": "user", "content": "Say hello to a new student in five words."}],
)

print(type(response).__name__)
for block in response.content:          # content is a LIST of blocks, not a string
    print(block.type, "->", block.text)
print("stop_reason:", response.stop_reason)
print("usage:", response.usage.input_tokens, "input tokens,", response.usage.output_tokens, "output tokens")