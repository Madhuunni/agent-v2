import json

from instruction_builder import build_instruction


def test_sample_login_prompt_returns_expected_json():
    prompt = "Navigate to http://localhost:4200/. Enter email and password. Click login."
    plan = build_instruction(prompt, "full_login_flow")
    output = json.loads(plan.model_dump_json())

    assert output["test_name"] == "Login Test"
    assert output["base_url"] == "http://localhost:4200/"
    assert [step["action"] for step in output["steps"]] == ["navigate", "type", "type", "click"]
    assert output["steps"][1]["value_from_env"] == "APP_EMAIL"
    assert output["steps"][2]["value_from_env"] == "APP_PASSWORD"
    assert output["steps"][3]["element"] == "login button"
