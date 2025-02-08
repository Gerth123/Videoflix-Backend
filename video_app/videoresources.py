from .admin import VideoResource

# Instanziiere die Resource
video_resource = VideoResource()

# Exportiere die Daten als Dataset
dataset = video_resource.export()

# Konvertiere das Dataset in JSON
json_data = dataset.json()

# Speichere das JSON in eine Datei
with open("videoresources.json", "w", encoding="utf-8") as file:
    file.write(json_data)

print("Daten wurden erfolgreich gespeichert!")