"""
Audio package exports.

The concrete audio backends are optional and are loaded lazily by
`audio.audio_capture.AudioCapture` so the rest of the app can start even when
native audio dependencies are unavailable.
"""

from audio.audio_capture import AudioCapture, create_audio_sender

__all__ = ["AudioCapture", "create_audio_sender"]
