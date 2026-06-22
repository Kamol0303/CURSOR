"""Print TOTP provisioning URI as an ASCII QR code in the terminal."""

from __future__ import annotations

from io import StringIO

import qrcode


def print_totp_qr(uri: str, *, username: str | None = None) -> None:
    """Render otpauth:// URI as a scannable QR in the terminal."""
    title = f"Google Authenticator QR — {username}" if username else "Google Authenticator QR"
    print(f"  {title}")
    print("  Telefon kamerasi yoki Authenticator ilovasi bilan skanerlang:")

    qr = qrcode.QRCode(border=1, box_size=1)
    qr.add_data(uri)
    qr.make(fit=True)

    buffer = StringIO()
    qr.print_ascii(invert=True, out=buffer)
    for line in buffer.getvalue().splitlines():
        print(f"  {line}")
