import discord
import requests
import base64
import asyncio

# Discord and GitHub settings
DISCORD_TOKEN = 'MTMwMTIyNTA3MTE3NTY2Nzc1Mw.Gf6kVK.ukOSUKFzgLOPaEqTQmaDVGER3bQqzN92vmcK0k'
CHANNEL_ID = 1188914354091991152  # Your Discord channel ID for updates
GITHUB_TOKEN = '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'  # Replace with your GitHub token
REPO_NAME = 'Dcannady03/discord-update-bot'  # Your GitHub repository path
FILE_PATH = 'update_notification.txt'  # File path in the repo
# Set up intents to allow message content access
# Set up intents to allow message content access
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


last_update_id = None  # Prevent duplicate updates


async def update_github_file(content):
    if not content.strip():  # Check if the content is empty
        print("Content is empty, nothing to update.")
        return
    
    url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    
    # Get the current file SHA (needed for updates)
    response = requests.get(url, headers=headers)
    sha = response.json().get("sha") if response.status_code == 200 else None

    # Prepare the data to create/update the file
    data = {
        "message": "Update from Discord bot",
        "content": base64.b64encode(content.encode()).decode(),  # Convert content to base64
        "sha": sha  # Include SHA if the file already exists
    }

    # Send PUT request to create/update the file
    result = requests.put(url, headers=headers, json=data)
    if result.status_code in [200, 201]:
        print("Successfully updated GitHub file.")
    else:
        print(f"Failed to update GitHub file: {result.json()}")

async def fetch_latest_messages():
    global last_update_id
    channel = client.get_channel(CHANNEL_ID)
    
    # List to store content of the last 3 messages
    recent_messages = []

    # Fetch the last 3 messages in the channel
    if channel:
        async for message in channel.history(limit=3):
            # Skip messages we've already processed
            if message.id == last_update_id:
                break

            # Set last_update_id to the ID of the most recent message processed
            last_update_id = message.id

            # Use message content, fallback to attachments or embeds if content is empty
            content = message.content.strip()
            if not content:
                # Check for attachments
                if message.attachments:
                    content = f"Attachment: {message.attachments[0].url}"
                # Check for embeds
                elif message.embeds:
                    embed_content = []
                    for embed in message.embeds:
                        embed_content.append(f"{embed.title or ''}\n{embed.description or ''}")
                    content = "\n\n".join(embed_content)
                # Default content if no text, attachments, or embeds
                else:
                    content = "No text content available in this message."

            # Append the content of each message to the recent_messages list
            recent_messages.append(content)

    # If there are new messages to process, concatenate and update the GitHub file
    if recent_messages:
        # Join messages with a divider to keep them visually separate
        combined_content = "\n\n---\n\n".join(recent_messages[::-1])  # Reverse order for most recent on top
        await update_github_file(combined_content)

@client.event
async def on_ready():
    print(f'Logged in as {client.user} and monitoring channel {CHANNEL_ID} for updates.')
    
    # Fetch the latest message once on startup
    await fetch_latest_messages()
    
    # Periodically check for new messages
    while True:
        await fetch_latest_messages()
        await asyncio.sleep(60)  # Check for new messages every 60 seconds

client.run(DISCORD_TOKEN)