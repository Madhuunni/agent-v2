import json

from instruction_builder import build_instruction, extract_url


def test_url_extraction():
    assert extract_url("Navigate to http://localhost:4200/. Login") == "http://localhost:4200/"


def test_email_password_steps_are_generated():
    plan = build_instruction("Enter email and password")
    elements = [step.element for step in plan.steps]
    assert "email" in elements
    assert "password" in elements
    assert any(step.value_from_env == "APP_EMAIL" for step in plan.steps)
    assert any(step.value_from_env == "APP_PASSWORD" for step in plan.steps)


def test_username_password_steps_are_generated():
    plan = build_instruction("Type username and password")
    elements = [step.element for step in plan.steps]
    assert "username" in elements
    assert "password" in elements
    assert any(step.value_from_env == "APP_USERNAME" for step in plan.steps)


def test_step_numbers_are_ordered():
    plan = build_instruction("Navigate to http://localhost:4200/ enter email and password click login")
    assert [step.step_no for step in plan.steps] == list(range(1, len(plan.steps) + 1))


def test_json_can_be_parsed():
    plan = build_instruction("Click submit")
    parsed = json.loads(plan.model_dump_json())
    assert parsed["steps"][0]["action"] == "click"
