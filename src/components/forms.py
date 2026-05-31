from __future__ import annotations

import fasthtml.common as ft


def FormGroup(label: str, field_id: str, *controls, cls: str = "form-group"):
    return ft.Div(
        ft.Label(label, fr=field_id),
        *controls,
        cls=cls,
    )


def TextInput(
    label: str,
    field_id: str,
    *,
    input_type: str = "text",
    required: bool = False,
    placeholder: str | None = None,
    cls: str = "form-group",
):
    return FormGroup(
        label,
        field_id,
        ft.Input(
            type=input_type,
            id=field_id,
            name=field_id,
            required=required,
            placeholder=placeholder,
            cls="form-input",
        ),
        cls=cls,
    )


def TextareaField(
    label: str,
    field_id: str,
    *,
    required: bool = False,
    rows: int = 5,
):
    return FormGroup(
        label,
        field_id,
        ft.Textarea(
            id=field_id,
            name=field_id,
            required=required,
            rows=rows,
            cls="form-input",
        ),
    )


def CaptchaField(captcha_image: str):
    return FormGroup(
        "Verification",
        "captcha",
        ft.Img(src=captcha_image, alt="CAPTCHA", cls="captcha-img"),
        ft.Input(
            type="text",
            id="captcha",
            name="captcha",
            required=True,
            placeholder="Enter the code above",
            cls="form-input",
        ),
    )
