"""Rule-assisted conversion from user prompts to validated JSON instructions."""

import re
from typing import Optional

from schema import InstructionPlan, InstructionStep

URL_RE = re.compile(r"https?://[^\s,.)]+/?")
EMAIL_SELECTOR = "input[type='email'], input[name='email'], input#email"
USERNAME_SELECTOR = "input[name='username'], input#username, input[type='text']"
PASSWORD_SELECTOR = "input[type='password'], input[name='password'], input#password"
LOGIN_SELECTOR = "button[type='submit'], button.login, #login"
SUBMIT_SELECTOR = "button[type='submit'], input[type='submit'], button.submit, #submit"
DASHBOARD_SELECTOR = "#dashboard, .dashboard, [data-testid='dashboard']"


def extract_url(prompt: str) -> Optional[str]:
    """Extract the first HTTP(S) URL from a prompt."""
    match = URL_RE.search(prompt)
    return match.group(0) if match else None


def _append_step(steps: list[InstructionStep], **kwargs) -> None:
    steps.append(InstructionStep(step_no=len(steps) + 1, **kwargs))


def build_instruction(prompt: str, predicted_intent: str = "unknown") -> InstructionPlan:
    """Build a deterministic, schema-validated instruction plan.

    The neural model supplies a broad intent, while these rules extract entities
    and compose the final JSON so execution output is predictable.
    """
    text = prompt.lower()
    steps: list[InstructionStep] = []
    base_url = extract_url(prompt)

    if base_url or "navigate" in text or "open" in text or "go to" in text:
        _append_step(
            steps,
            action="navigate",
            element=None,
            by=None,
            selector=None,
            value=base_url,
            value_from_env=None,
            description="Navigate to the application URL",
        )

    wants_username = "username" in text or "user name" in text
    wants_email = "email" in text or ("login" in text and not wants_username)
    wants_password = "password" in text or "login" in text

    if wants_email:
        _append_step(
            steps,
            action="type",
            element="email",
            by="css selector",
            selector=EMAIL_SELECTOR,
            value=None,
            value_from_env="APP_EMAIL",
            description="Enter email from environment variable APP_EMAIL",
        )
    if wants_username:
        _append_step(
            steps,
            action="type",
            element="username",
            by="css selector",
            selector=USERNAME_SELECTOR,
            value=None,
            value_from_env="APP_USERNAME",
            description="Enter username from environment variable APP_USERNAME",
        )
    if wants_password:
        _append_step(
            steps,
            action="type",
            element="password",
            by="css selector",
            selector=PASSWORD_SELECTOR,
            value=None,
            value_from_env="APP_PASSWORD",
            description="Enter password from environment variable APP_PASSWORD",
        )

    if "submit" in text:
        _append_step(
            steps,
            action="click",
            element="submit button",
            by="css selector",
            selector=SUBMIT_SELECTOR,
            value=None,
            value_from_env=None,
            description="Click the submit button",
        )
    elif "login" in text or "log in" in text or "sign in" in text:
        _append_step(
            steps,
            action="click",
            element="login button",
            by="css selector",
            selector=LOGIN_SELECTOR,
            value=None,
            value_from_env=None,
            description="Click the login button",
        )

    if "dashboard" in text and ("verify" in text or "visible" in text or "see" in text):
        _append_step(
            steps,
            action="verify_visible",
            element="dashboard",
            by="css selector",
            selector=DASHBOARD_SELECTOR,
            value=None,
            value_from_env=None,
            description="Verify the dashboard is visible",
        )

    if not steps:
        _append_step(
            steps,
            action="verify_visible",
            element="page",
            by="tag name",
            selector="body",
            value=None,
            value_from_env=None,
            description=f"Fallback visible-page check for predicted intent: {predicted_intent}",
        )

    test_name = "Login Test" if any(s.element in {"email", "username", "password", "login button"} for s in steps) else "Browser Instruction Test"
    return InstructionPlan(test_name=test_name, base_url=base_url, steps=steps)
