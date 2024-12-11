from doubt import discord_logging
from tqdm import tqdm
import time

WEBHOOK_URL = "https://discord.com/api/webhooks/1316467098884771850/LorKoIV2JHRCzEbNXEJMU8MWAP0vy9dSY0wIRtWGmNZl8zHMyuRmIqHCcmJsElmvBgoG"

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
