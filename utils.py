import os

def mac_notify(title, text):
    os.system(f'say "{title}"')
    os.system(f"osascript -e 'display notification \"{text}\" with title \"{title}\"'")
