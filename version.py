import requests
import argparse
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

def fetch_data():
    url = "https://internal-tool.dev.theixt.com/server-info/api/info"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Fail: {response.status_code}")
        return None

def classify_server(server_name):
    parts = server_name.split()
    first_word = parts[0].lower()
    if len(parts) < 2:
        if first_word == "cms" :
            display_name = "Launchpad"
            return "BE Standard API", display_name
        elif first_word == "cat" :
            display_name = first_word.upper()
            return "BE Standard API", display_name
        else :
            return None, None

    second_word = parts[1]

    if first_word in ["core", "internal"]:
        display_name = "Core"
        if second_word == "WEB":
            return "FE Service", display_name
        elif second_word == "API":
            return "BE Standard API", display_name
        elif second_word == "GW":
            return "BE Gateway", display_name
    elif first_word == "cms":
        display_name = "Launchpad"
        if second_word == "WEB":
            return "FE Service", display_name
    elif first_word == "prm":
        display_name = first_word.upper()
        if second_word == "WEB":
            return "FE Service", display_name
        elif second_word == "API":
            return "BE internal-API", display_name
        elif len(parts) > 2 and parts[1:3] == ["STD", "API"]:
            return "BE Standard API", display_name
        elif second_word == "GW":
            return "BE Gateway", display_name
    elif first_word == "ixt":
        display_name = second_word.capitalize()
        if parts[2] == "WEB":
            return "FE Service", display_name
    elif first_word in ["claim", "auth", "system", "event"]:
        display_name = first_word.capitalize()
        if second_word == "WEB":
            return "FE Service", display_name
        elif second_word == "API":
            return "BE Standard API", display_name
        elif second_word == "GW":
            return "BE Gateway", display_name
    else:
        display_name = parts[0].capitalize()
        if second_word == "WEB":
            return "FE Service", display_name
        elif second_word == "API" :
            return "BE internal-API", display_name
        elif len(parts) > 2 and parts[1:3] == ["INTERNAL", "API"]:
            return "BE internal-API", display_name
        elif len(parts) > 2 and parts[1:3] == ["STD", "API"]:
            return "BE Standard API", display_name
        elif second_word == "GW":
            return "BE Gateway", display_name
    return None, None

def markdown_to_image(markdown_table, output_path):
    lines = markdown_table.strip().split("\n")
    headers = [header.strip() for header in lines[0].split("|")[1:-1]]
    data = [line.split("|")[1:-1] for line in lines[2:]]
    df = pd.DataFrame(data, columns=headers)

    fig, ax = plt.subplots(figsize=(len(headers) * 2, len(df) * 0.28))
    ax.set_facecolor("black")
    ax.axis("tight")
    ax.axis("off")
    table = ax.table(
        cellText=df.values,
        colLabels=df.columns,
        cellLoc="center",
        loc="center",
    )

    table.auto_set_font_size(False)
    table.set_fontsize(100)
    table.auto_set_column_width(col=list(range(len(headers))))

    for (row, col), cell in table.get_celld().items():
        cell.set_edgecolor("white") 
        cell.set_linewidth(1)
        cell.set_height(1.9) 
        if row == 0:  
            cell.set_facecolor("black")
            cell.set_text_props(weight="bold", color="white", ha="center", va="center")
        else:  # 表內容樣式
            cell.set_facecolor("black")
            cell.set_text_props(weight="bold", color="white", ha="center", va="center")


    plt.savefig(output_path, bbox_inches="tight", dpi=30)
    plt.close()

def main(environment):
    data = fetch_data()
    if data is None:
        return

    categorized_data = {
        "FE Service": {},
        "BE internal-API": {},
        "BE Standard API": {},
        "BE Gateway": {}
    }

    services = []

    for item in data:
        server_name = item.get("server_name", "")
        version_info = item.get(environment, {})
        version = version_info.get("version", "-")
        
        category, display_name = classify_server(server_name)
        if category:
            if display_name not in services:
                services.append(display_name)
            categorized_data[category][display_name] = version

    markdown_table = "| Service | FE Service | BE internal-API | BE Standard API | BE Gateway |\n"
    markdown_table += "|---------|------------|-----------------|-----------------|------------|\n"

    for service in services:
        row = [service]
        for category in ["FE Service", "BE internal-API", "BE Standard API", "BE Gateway"]:
            row.append(categorized_data[category].get(service, "-"))
        markdown_table += "| " + " | ".join(row) + " |\n"

    with open("test.md", "w") as f:
        f.write(markdown_table)

    desktop_path = Path.home() / "Desktop" / "version.png"
    markdown_to_image(markdown_table, desktop_path)

    print(f"Done! Table image saved to {desktop_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Fetch version info for specified environment.')
    parser.add_argument('-env', '--environment', choices=['dev', 'dev2', 'sit', 'sit2'], required=True, help='Environment to fetch version from')
    args = parser.parse_args()

    main(args.environment)

    # 指令：python3 version.py -env sit
