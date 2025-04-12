from .admin import VideoResource

video_resource = VideoResource()

dataset = video_resource.export()

json_data = dataset.json()

with open("videoresources.json", "w", encoding="utf-8") as file:
    file.write(json_data)

print("Daten wurden erfolgreich gespeichert!")
