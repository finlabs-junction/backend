from __future__ import annotations

import os

import msgspec
from msgspec import Struct


class StripeSettings(Struct):
    secret_key: str = os.environ.get(
        "QS_STRIPE_SECRET_KEY",
        "",
    )
    """
    Stripe secret key.
    """

    publishable_key: str = os.environ.get(
        "QS_STRIPE_PUBLISHABLE_KEY",
        "",
    )
    """
    Stripe publishable key.
    """

    endpoint_secret: str = os.environ.get(
        "QS_STRIPE_ENDPOINT_SECRET",
        "",
    )
    """
    Stripe endpoint secret.
    """

    success_path: str = os.environ.get(
        "QS_STRIPE_SUCCESS_PATH",
        "/api/schema",
    )
    """
    Stripe success URL path.
    """

    cancel_path: str = os.environ.get(
        "QS_STRIPE_CANCEL_PATH",
        "/api/schema",
    )
    """
    Stripe cancel URL path.
    """


class StripeSettingsMixin(Struct):
    stripe: StripeSettings = msgspec.field(default_factory=StripeSettings)
    """
    Stripe settings.
    """
