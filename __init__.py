# Checkpoint Automatic Config
# Created by DarkDinDoN
import os
import yaml
import comfy.samplers
from nodes import CheckpointLoaderSimple, MAX_RESOLUTION


# Load checkpoint configuration
def readConfigFile(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)


# Validate checkpoint configuration
def validateCheckpointConfig(config):
    if not {"steps_total", "cfg", "sampler_name", "scheduler_name"} <= config.keys():
        raise Exception(
            "Automatic checkpoint configuration: missing key(s)/value(s) in the configuration file!")

    if not isinstance(config["steps_total"], int) or config["steps_total"] < 1 or config["steps_total"] > MAX_RESOLUTION:
        raise Exception(
            f"Automatic checkpoint configuration: invalid \"steps_total\" format!", f"Got \"{config['steps_total']}\".")

    if not isinstance(config["cfg"], float) or config["cfg"] < 0.0 or config["cfg"] > 100.0:
        raise Exception(
            f"Automatic checkpoint configuration: invalid \"cfg\" format! Got \"{config['cfg']}\".")

    if not config["sampler_name"] in comfy.samplers.SAMPLER_NAMES:
        raise Exception(
            f"Automatic checkpoint configuration: invalid \"sampler_name\" format! Got \"{config['sampler_name']}\".")

    if not config["scheduler_name"] in comfy.samplers.SCHEDULER_NAMES:
        raise Exception(
            f"Automatic checkpoint configuration: invalid \"scheduler_name\" format! Got \"{config['scheduler_name']}\".")


# Globals
script_dir = os.path.dirname(__file__)
config_file = readConfigFile(os.path.join(script_dir, "models_config.yaml"))


# Node
class CheckpointAutomaticConfig(CheckpointLoaderSimple):
    @classmethod
    def INPUT_TYPES(s):
        types = super().INPUT_TYPES()
        types["required"].update({
            "automatic_config": ("BOOLEAN", {"default": True}),
            "steps_total": ("INT", {
                "default": 5,
                "min": 1,
                "max": MAX_RESOLUTION,
                "step": 1,
            }),
            "cfg": ("FLOAT", {
                    "default": 2.0,
                    "min": 0.0,
                    "max": 100.0,
                    "step": 0.1,
                    }),
            "sampler_name": (comfy.samplers.SAMPLER_NAMES,),
            "scheduler_name": (comfy.samplers.SCHEDULER_NAMES,),
        })
        return types

    RETURN_TYPES = CheckpointLoaderSimple.RETURN_TYPES + (
        "INT",
        "FLOAT",
        comfy.samplers.KSampler.SAMPLERS,
        comfy.samplers.KSampler.SCHEDULERS
    )

    RETURN_NAMES = CheckpointLoaderSimple.RETURN_TYPES + (
        "STEPS",
        "CFG",
        "SAMPLER",
        "SCHEDULER"
    )

    def load_checkpoint(self, automatic_config, steps_total, cfg, sampler_name, scheduler_name, **kwargs):
        if automatic_config:
            if kwargs["ckpt_name"] in config_file:
                # Validate first
                validateCheckpointConfig(config_file[kwargs["ckpt_name"]])

                # Assign new values
                steps_total = config_file[kwargs["ckpt_name"]]["steps_total"]
                cfg = config_file[kwargs["ckpt_name"]]["cfg"]
                sampler_name = config_file[kwargs["ckpt_name"]]["sampler_name"]
                scheduler_name = config_file[kwargs["ckpt_name"]
                                             ]["scheduler_name"]

                # print assigned values
                print(
                    f"======== Applying checkpoint automatic configuration: steps: {steps_total} | cfg: {cfg} | sampler: {sampler_name} | scheduler: {scheduler_name} ========")
            else:
                raise Exception(
                    "Automatic checkpoint configuration: unknown checkpoint. Disable \"automatic_config\" to use this checkpoint.")

        out = super().load_checkpoint(**kwargs)
        return out + (
            steps_total,
            cfg,
            sampler_name,
            scheduler_name
        )

    CATEGORY = "Checkpoint Config Loader"


NODE_CLASS_MAPPINGS = {
    "CheckpointAutomaticConfig": CheckpointAutomaticConfig
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "CheckpointAutomaticConfig": "Checkpoint Automatic Config"
}
