import os
from dotenv import load_dotenv
import replicate

from config import REPLICATE_MODELS

load_dotenv()

REPLICATE_API_KEY = os.getenv("REPLICATE_API_KEY")

replicate_client = replicate.Client(api_token=REPLICATE_API_KEY)


async def inpaint_image_replicate(image_url, mask_url):
    print(REPLICATE_MODELS["viper"]["id"])
    try:
        output = await replicate_client.async_run(
            REPLICATE_MODELS["viper"]["id"],
            input={
                "mask": mask_url,
                "image": image_url,
                "width": 512,
                "height": 512,
                "prompt": REPLICATE_MODELS["viper"]["initialPrompt"],
                "refine": "no_refiner",
                "scheduler": "KarrasDPM",
                "lora_scale": 0.8,
                "num_outputs": 1,
                "guidance_scale": 4,
                "apply_watermark": False,
                "high_noise_frac": 0.8,
                "negative_prompt": "longbody, lowres, bad anatomy, bad hands, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality",
                "prompt_strength": 0.6,
                "num_inference_steps": 25,
            },
        )
        return output

    except Exception as e:
        print("Error while inpainting the image", e)
