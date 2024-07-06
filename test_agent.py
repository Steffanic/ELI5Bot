import pytest

from responder_agent import build_agent as responder
from evaluator_agent import build_agent as evaluator

def test_responder_agent():
    question = "ELI5: How did American soldiers use napalm without harming themselves? "
    response = responder().chat(question)
    assert response is not None
    print(response)

def test_evaluator_agent():
    question = "ELI5: How did American soldiers use napalm without harming themselves?"
    bad_answer = "You ever see one of those little cans with the pink gel in them that you light to keep a serving tray warm? Thats napalm and its fairly harmless until given oxygen and heated above its ingition point."
    good_answer = "Napalm was powerful but I think the main culprit of chemicals they were exposed to that left lasting health damage was Agent Orange. My grandfather had a grapefruit sized tumor in his lung when he died on the operating table from the surgeon accidently cutting an artery. That wasn't his only health problem, either. He started to hunch over with arthritis in his neck and spine to the point it affected his height, and it didn't look like normal aging stuff anyway. He was maybe in his 50s but his health was like 20-30 years older seeming. I don't know more details because he died before I was born but his health spiraled from exposure to that stuff."
    response = responder().chat(question)
    assert response is not None
    print(response)

    evaluation = evaluator().chat(f"Question: {question} Answer: {response}")
    assert evaluation is not None
    print(f"Responder Evaluation: {evaluation}")

    evaluation = evaluator().chat(f"Question: {question} Answer: {bad_answer}")
    assert evaluation is not None
    print(f"Bad Answer Evaluation: {evaluation}")

    evaluation = evaluator().chat(f"Question: {question} Answer: {good_answer}")
    assert evaluation is not None
    print(f"Good Answer Evaluation: {evaluation}")