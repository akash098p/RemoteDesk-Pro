"""
===============================================================================
RemoteDesk Pro
File: audio/sounddevice_capture.py
Real-time audio capture using SoundDevice (cross-platform alternative to PyAudio)
===============================================================================
"""

import threading
import time
import queue
import logging
from typing import Optional, Callable

import sounddevice as sd
import numpy as np

logger = logging.getLogger(__name__)

class SoundDeviceCapture:
    """
    Audio capture using SoundDevice library
    More reliable cross-platform alternative to PyAudio
    """
    
    def __init__(
        self,
        rate: int = 16000,
        chunk: int = 1024,
        channels: int = 1,
        on_audio_data: Optional[Callable[[bytes], None]] = None
    ):
        """
        Initialize sound device capture
        
        Args:
            rate: Sample rate (Hz)
            chunk: Frames per buffer
            channels: Number of audio channels
            on_audio_data: Callback for processed audio data
        """
        self.rate = rate
        self.chunk = chunk
        self.channels = channels
        self.on_audio_data = on_audio_data
        
        self._running = False
        self._stream = None
        self._audio_queue = queue.Queue(maxsize=50)
    
    def start(self) -> bool:
        """Start audio capture"""
        if self._running:
            return True
        
        try:
            self._stream = sd.InputStream(
                samplerate=self.rate,
                channels=self.channels,
                blocksize=self.chunk,
                callback=self._audio_callback
            )
            self._stream.start()
            self._running = True
            logger.info(f"SoundDevice capture started (rate={self.rate})")
            return True
        except Exception as e:
            logger.error(f"Failed to start SoundDevice capture: {e}")
            return False
    
    def _audio_callback(self, indata: np.ndarray, frames: int, time, status):
        """Audio callback function"""
        if self._running and indata is not None:
            # Convert numpy array to bytes
            audio_bytes = indata.tobytes()
            
            # Send via callback
            if self.on_audio_data:
                try:
                    self.on_audio_data(audio_bytes)
                except Exception as e:
                    logger.error(f"Audio callback error: {e}")
            
            # Add to queue
            try:
                self._audio_queue.put_nowait(audio_bytes)
            except queue.Full:
                # Drop oldest frame
                try:
                    self._audio_queue.get_nowait()
                    self._audio_queue.put_nowait(audio_bytes)
                except queue.Empty:
                    pass
    
    def stop(self):
        """Stop audio capture"""
        self._running = False
        if self._stream:
            self._stream.stop()
            self._stream.close()
        logger.info("SoundDevice capture stopped")
    
    def get_audio_chunk(self, timeout: float = 0.1) -> Optional[bytes]:
        """Get audio chunk from queue"""
        try:
            return self._audio_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def is_running(self) -> bool:
        return self._running


def create_sounddevice_capture(
    rate: int = 16000,
    chunk: int = 1024,
    channels: int = 1,
    on_audio_data: Optional[Callable[[bytes], None]] = None
) -> SoundDeviceCapture:
    """Factory function to create a SoundDeviceCapture instance"""
    return SoundDeviceCapture(
        rate=rate,
        chunk=chunk,
        channels=channels,
        on_audio_data=on_audio_data
    )