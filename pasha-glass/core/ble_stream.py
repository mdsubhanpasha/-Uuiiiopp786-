"""
Ray-Ban Meta Glasses BLE Stream Simulation Pipeline.
Simulates receiving camera frame buffers from Ray-Ban Meta Glasses over Bluetooth Low Energy (BLE).
"""

import time
import cv2
import numpy as np
from typing import Dict, Any, Generator, Tuple, Optional


class MetaGlassesBLEStream:
    """
    Simulates BLE connection and stream receiving pipeline from Ray-Ban Meta Glasses companion app.
    """

    def __init__(self, device_name: str = "Ray-Ban Meta Glasses [BLE-0482]"):
        self.device_name = device_name
        self.is_connected = False
        self.frame_counter = 0

    def connect(self) -> bool:
        """Establish simulated BLE pairing with Meta Glasses."""
        self.is_connected = True
        return True

    def disconnect(self) -> bool:
        """Disconnect BLE pairing."""
        self.is_connected = False
        return False

    def generate_synthetic_frame(
        self,
        text: str = "Meta Glasses Camera Feed",
        add_face: bool = True
    ) -> Tuple[np.ndarray, Optional[Tuple[int, int, int, int]]]:
        """
        Generates a synthetic camera frame simulating HUD video feed.
        """
        self.frame_counter += 1
        frame = np.full((480, 640, 3), (30, 30, 30), dtype=np.uint8)

        # Draw header overlay simulation
        cv2.putText(
            frame,
            f"BLE STREAM: {self.device_name} | Frame #{self.frame_counter}",
            (20, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0),
            2
        )

        bbox = None
        if add_face:
            # Draw a face shape in center
            cx, cy = 320, 240
            cv2.circle(frame, (cx, cy), 80, (200, 200, 200), -1)
            # Eyes & mouth
            cv2.circle(frame, (cx - 30, cy - 20), 10, (50, 50, 50), -1)
            cv2.circle(frame, (cx + 30, cy - 20), 10, (50, 50, 50), -1)
            cv2.ellipse(frame, (cx, cy + 30), (30, 15), 0, 0, 180, (50, 50, 50), 3)

            bbox = (cx - 80, cy - 80, 160, 160)

        cv2.putText(
            frame,
            text,
            (20, 450),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )

        return frame, bbox

    def frame_stream_generator(self, count: int = 5) -> Generator[Dict[str, Any], None, None]:
        """
        Yields camera frame payloads received over BLE stream.
        """
        if not self.is_connected:
            self.connect()

        for i in range(count):
            frame, bbox = self.generate_synthetic_frame(text=f"Live Feed Segment #{i+1}")
            yield {
                "frame_id": f"ble_frame_{self.frame_counter}",
                "timestamp": time.time(),
                "frame_bytes": frame,
                "bbox_hint": bbox
            }
