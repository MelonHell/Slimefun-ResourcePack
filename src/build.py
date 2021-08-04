import json
import yaml
import shutil
from pathlib import Path

# CONFIG

namespace = "sf"
skip_none = True
short_names = True

# CODE

with open("item-models.yml", "r") as f:
    item_models = yaml.safe_load(f)

with open("items.yml", "r") as f:
    items = yaml.safe_load(f)

minecraft_models_path = Path("../assets/minecraft/models/item/")
vanilla_models_path = Path("minecraft/models/item/")

shutil.rmtree("../assets", ignore_errors=True)
minecraft_models_path.mkdir(parents=True)

it_keys = list(items.keys())
it_keys.sort(key=lambda e: item_models[e])

c = 0

for item in it_keys:
    print(item)
    for id, texture in enumerate(items[item]["textures"]):
        if skip_none and texture == "item/none":
            continue
        texture_src = Path("textures/").joinpath(texture + ".png")
        if short_names:
            new_texture = str(c)
            c += 1
        else:
            new_texture = texture
        custom_model_data = item_models[item]
        material = items[item]["item"]

        # COPY TEXTURES
        texture_path = Path(f"../assets/{namespace}/textures/").joinpath(new_texture + ".png")
        texture_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(texture_src, texture_path)
        meta_src = texture_src.parent.joinpath(texture_src.name + ".mcmeta")
        meta_path = texture_path.parent.joinpath(texture_path.name + ".mcmeta")
        if meta_src.exists():
            shutil.copyfile(meta_src, meta_path)

        # MAKE TEXTURE JSON
        model_type = items[item]["model"]
        with open(f"models/{model_type}.json", "r") as f:
            model = json.load(f)
        for i in model["textures"]:
            model["textures"][i] = f"{namespace}:{new_texture}"
        json_path = Path(f"../assets/{namespace}/models/").joinpath(new_texture + ".json")
        json_path.parent.mkdir(parents=True, exist_ok=True)
        with open(json_path, "w") as f:
            json.dump(model, f)

        # MINECRAFT JSON GENERATOR
        if minecraft_models_path.joinpath(f"{material}.json").exists():
            with open(minecraft_models_path.joinpath(f"{material}.json"), "r") as f:
                material_model = json.load(f)
        else:
            with open(vanilla_models_path.joinpath(f"{material}.json"), "r") as f:
                material_model = json.load(f)

        if "overrides" not in material_model:
            material_model["overrides"] = []

        if id == 0:
            material_model["overrides"].append({"predicate": {"custom_model_data": custom_model_data}, "model": f"{namespace}:{new_texture}"})

        if material == "bow":
            if id == 1:
                material_model["overrides"].append({"predicate": {"custom_model_data": custom_model_data, "pulling": 1}, "model": f"{namespace}:{new_texture}"})
            if id == 2:
                material_model["overrides"].append({"predicate": {"custom_model_data": custom_model_data, "pulling": 1, "pull": 0.65}, "model": f"{namespace}:{new_texture}"})
            if id == 3:
                material_model["overrides"].append({"predicate": {"custom_model_data": custom_model_data, "pulling": 1, "pull": 0.9}, "model": f"{namespace}:{new_texture}"})

        elif material == "elytra":
            if id == 1:
                material_model["overrides"].append({"predicate": {"custom_model_data": custom_model_data, "broken": 1}, "model": f"{namespace}:{new_texture}"})

        with open(minecraft_models_path.joinpath(f"{material}.json"), "w") as f:
            json.dump(material_model, f)

