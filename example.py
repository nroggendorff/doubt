from doubt.doubt import discord_logging
from tqdm import tqdm
import time

import os

WEBHOOK_URL = f"https://discord.com/api/webhooks/{os.getenv('WEBHOOK_ID')}/{os.getenv('WEBHOOK_TOKEN')}"

@discord_logging(webhook_url=WEBHOOK_URL, app_name="MyApp")
def my_function():
    print("Processing...")

    for _ in tqdm(range(100), desc="Processing"):
        time.sleep(0.1)

        # if _ == 60:
        #     raise ValueError("Test error")

    print("Processing complete!")

if __name__ == "__main__":
    my_function()  
