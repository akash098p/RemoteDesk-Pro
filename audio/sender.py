"""
===============================================================================
RemoteDesk Pro
File: audio/sender.py
Audio sending and transmission component
===============================================================================
"""

import threading
import time
import queue
import logging
from typing import Optional, Callable

import pyaudio

logger = logging.getLogger(__name__)

class AudioSender:
    """
    Real-time audio sender for RemoteDesk Pro
    Captures microphone input and transmits it over the network
    """
    
    def __init__(
        self,
        rate: int = 16000,
        chunk: int = 1024,
        channels: int = 1,
        on_audio_data: Optional[Callable[[bytes], None]] = None
    ):
        """
        Initialize audio sender
        
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
        self._capture_thread = None
        self._audio = None
        self._stream = None
        
        # Audio queue for buffering
        self._audio_queue = queue.Queue(maxsize=50)
    
    def start(self) -> bool:
        """Start audio capture"""
        if self._running:
            logger.warning("Audio sender is already running")
            return True
        
        try:
            self._audio = pyaudio.PyAudio()
            
            # Find default input device
            device_index = None
            for i in range(self._audio.get_device_count()):
                device_info = self._audio.get_device_info_by_index(i)
                if device_info['maxInputChannels'] > 0:
                    device_index = i
                    break
            
            self._stream = self._audio.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk,
                input_device_index=device_index
            )
            
            self._running = True
            self._capture_thread = threading.Thread(
                target=self._capture_loop,
                name="AudioSenderThread",
                daemon=True
            )
            self._capture_thread.start()
            logger.info(f"Audio sender started (rate={self.rate}, chunk={self.chunk})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start audio sender: {e}")
            return False
    
    def stop(self) -> None:
        """Stop audio capture"""
        self._running = False
        
        if self._stream:
            try:
                self._stream.stop_stream()
                self._stream.close()
            except:
                pass
        
        if self._audio:
            try:
                self._audio.terminate()
            except:
                pass
        
        logger.info("Audio sender stopped")
    
    def _capture_loop(self) -> None:
        """Main audio capture loop"""
        while self._running:
            try:
                data = self._stream.read(self.chunk, exception_on_overflow=False)
                
                # Send via callback
                if self.on_audio_data:
                    try:
                        self.on_audio_data(data)
                    except Exception as e:
                        logger.error(f"Error in on_audio_data callback: {e}")
                
                # Add to queue for backup
                try:
                    self._audio_queue.put_nowait(data)
                except queue.Full:
                    # Drop oldest frame if queue is full
                    try:
                        self._audio_queue.get_nowait()
                        self._audio_queue.put_nowait(data)
                    except queue.Empty:
                        pass
                
                time.sleep(0.001)  # Small delay to prevent high CPU usage
                
            except Exception as e:
                if self._running:
                    logger.error(f"Audio capture error: {e}")
    
    def get_audio_chunk(self, timeout: float = 0.1) -> Optional[bytes]:
        """Get audio chunk from queue"""
        try:
            return self._audio_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def is_running(self) -> bool:
        return self._running
    
    def get_stats(self) -> dict:
        """Get sender statistics"""
        return {
            "running": self._running,
            "rate": self.rate,
            "chunk": self.chunk,
            "channels": self.channels,
            "queue_size": self._audio_queue.qsize()
        }


def create_audio_sender(
    rate: int = 16000,
    chunk: int = 1024,
    channels: int = 1,
    on_audio_data: Optional[Callable[[bytes], None]] = None
) -> AudioSender:
    """
    Factory function to create an AudioSender instance
    
    Args:
        rate: Sample rate (Hz)
        chunk: Frames per buffer
        channels: Number of audio channels
        on_audio_data: Callback for processed audio data
        
    Returns:
        Configured AudioSender instance
    """
    return AudioSender(
        rate=rate,
        chunk=chunk,
        channels=channels,
        on_audio_data=on_audio_data
    )