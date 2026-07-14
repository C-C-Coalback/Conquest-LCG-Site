import os


replacements = [("Call the Storm", "Call The Storm"),
                ("Command-Link Drone", "Command-link Drone"), 
                ("Lucky Shot", "Promethium Mine"), 
                ("Amalgamated Devotee", "Promethium Mine"), 
                ("The Phalanx", "Promethium Mine"), 
                ("Imperial Fists Legion", "Promethium Mine"), 
                ("Bladeguard Veteran Squad", "Promethium Mine"), 
                ("Reeducation Protocol", "Promethium Mine"), 
                ("Kroot Infiltrator", "Promethium Mine"), 
                ("Fire Caste Cadre", "Promethium Mine"), 
                ("Rapid Ingress", "Promethium Mine"), 
                ("Storm Guardians", "Promethium Mine"), 
                ("Incubus of the Severed", "Promethium Mine"),
                ("The Price of Success", "Promethium Mine"), 
                ("Chaos Maulerfiend", "Promethium Mine"), 
                ("Palace of Slaanesh", "Promethium Mine"), 
                ("Khornate Heldrake", "Promethium Mine"), 
                ("Abrasive Squigherder", "Promethium Mine"), 
                ("Baddfrag", "Promethium Mine"), 
                ("Necklace of Teef", "Promethium Mine"), 
                ("Speed Freakz Warpaint", "Promethium Mine"),
                ("Unearthed Crypt", "Promethium Mine"), 
                ("Harbinger of the Storm", "Promethium Mine"), 
                ("Fabricator Claw Array", "Promethium Mine"), 
                ("Repurposed Pariah", "Promethium Mine"), 
                ("Disruption Field", "Promethium Mine")]


cwd = os.getcwd()
print(cwd)
target_directory = cwd + "/decks/DeckStorage/"
for file in os.listdir(target_directory):
    creator = target_directory + file
    creator_file = creator + "/"
    for deck_name in os.listdir(creator_file):
        print(creator_file + deck_name)
        content_file = creator_file + deck_name
        with open(content_file, "r") as f:
            content = f.read()
        for i in range(len(replacements)):
            content = content.replace(replacements[i][0], replacements[i][1])
        with open(content_file, "w") as f:
            f.write(content)
