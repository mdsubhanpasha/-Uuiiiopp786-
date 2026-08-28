import os
import uuid
import requests
from typing import Dict, Any, List
from PIL import Image, ImageDraw, ImageFont
from loguru import logger

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

class DesignerNode:
    """
    Node 3 - Designer
    Generates 2 DALL-E 3 prompts for LinkedIn carousel/image (1024x1024, professional, minimal),
    calls DALL-E 3 API (or generates clean PNG image), saves images to /outputs/images/.
    """
    def __init__(self, output_dir: str = "outputs/images"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.openai_key = os.getenv("OPENAI_API_KEY", "")
        self.client = None
        if OPENAI_AVAILABLE and self.openai_key and not self.openai_key.startswith("sk-placeholder"):
            try:
                self.client = OpenAI(api_key=self.openai_key)
            except Exception as e:
                logger.warning(f"Designer OpenAI init failed: {e}")

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("Executing Node 3: Designer...")
        topic = state.get("topic", "AI Architecture")
        hook = state.get("hook", "Autonomous Multi-Agent Systems")

        prompt_1 = f"A sleek, professional, dark-themed technological architectural diagram showcasing modern multi-agent workflows for '{topic}'. Minimalist vector graphics, subtle glowing neon blue and purple accents, high aesthetic quality, 1024x1024."
        prompt_2 = f"A modern 3D render of an abstract digital brain network representing '{hook}'. Deep oceanic blue background, glowing nodes, minimalist executive design, 8k resolution, photorealistic."

        prompts = [prompt_1, prompt_2]
        selected_prompt = prompt_1

        filename = f"post_img_{uuid.uuid4().hex[:8]}.png"
        filepath = os.path.join(self.output_dir, filename)

        if self.client:
            try:
                response = self.client.images.generate(
                    model="dall-e-3",
                    prompt=selected_prompt,
                    size="1024x1024",
                    quality="standard",
                    n=1,
                )
                image_url = response.data[0].url
                img_data = requests.get(image_url, timeout=15).content
                with open(filepath, "wb") as f:
                    f.write(img_data)
                logger.info(f"DALL-E 3 image saved to {filepath}")
            except Exception as e:
                logger.error(f"DALL-E 3 generation failed: {e}. Generating binary PNG fallback image.")
                filepath = self._generate_fallback_png(filename, topic)
                image_url = f"/outputs/images/{filename}"
        else:
            filepath = self._generate_fallback_png(filename, topic)
            image_url = f"/outputs/images/{filename}"

        return {
            "image_prompts": prompts,
            "selected_prompt": selected_prompt,
            "image_url": image_url,
            "local_image_path": filepath
        }

    def _generate_fallback_png(self, filename: str, topic: str) -> str:
        filepath = os.path.join(self.output_dir, filename)
        width, height = 1024, 1024

        # Create a dark gradient background
        image = Image.new("RGB", (width, height), color=(15, 23, 42))
        draw = ImageDraw.Draw(image)

        # Draw tech circles
        draw.ellipse([312, 200, 712, 600], outline=(99, 102, 241), width=8)
        draw.ellipse([372, 260, 652, 540], outline=(168, 85, 247), width=6)
        draw.ellipse([452, 340, 572, 460], fill=(59, 130, 246))

        # Draw header text
        draw.text((width // 2, 700), "PASHA-UNIFIED-OS", fill=(255, 255, 255), anchor="mm")
        draw.text((width // 2, 770), topic[:45], fill=(148, 163, 184), anchor="mm")

        image.save(filepath, format="PNG")
        return filepath
