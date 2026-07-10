"""
===============================================================================
RemoteDesk Pro
File: audio/receiver.py
AudioReceive buffer manager
"""

import queue
import logging
from threading import Thread

class AudioReceiver:
    """Manages incoming audio data from remote devices"""
    
    def __init__(self):
        self._audio_queue = queue.Queue(maxsize=20)
        self._playback_enabled = True
        self._running = False
        self._stream = None
        self._sample_rate = 16000
        self._channels = 1
    
    def start(self):
        """Start receiving audio data"""
        self._running = True
        self._playback_thread = Thread(target=self._playback_loop, daemon=True)
        self._playback_thread.start()
        logging.info("Audio receiver started")
    
    def stop(self):
        """Stop receiving audio data"""
        self._running = False
        logger.info("Audio receiver stopped")
    
    def enqueue_data(self, data: bytes):
        """Add received audio data to queue"""
        try:
            self._audio_queue.put_nowait(data)
        except queue.Full:
            pass  # Drop oldest data if queue is full
    
    def _playback_loop(self):
        """Audio playback loop"""
        try:
            # This would normally play the audio
            while self._running:
                try:
                    data = self._audio_queue.get(timeout=0.1)
                    # Here we would use PyAudio to play the data
                    print("Playing audio:", len(data), "bytes")
                except queue.Empty:
                    pass
        except Exception as e:
                    print(f"Audio playback error: {e}")
    
    def get_queue_size(self) -> int:
        """Get current queue size"""
        return self._audio_queue.qsize()

audio_receiver = AudioReceiver()