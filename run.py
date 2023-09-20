import modal, os, sys, shlex

stub = modal.Stub("stable-diffusion-comfyui")
volume = modal.NetworkFileSystem.new().persisted("stable-diffusion-comfyui")

@stub.function(
    image=modal.Image.from_registry("nvidia/cuda:12.2.0-base-ubuntu22.04", add_python="3.11")
    .run_commands(
        "apt update -y && \
        apt install -y software-properties-common && \
        apt update -y && \
        add-apt-repository -y ppa:git-core/ppa && \
        apt update -y && \
        apt install -y git git-lfs && \
        git --version  && \
        apt install -y aria2 libgl1 libglib2.0-0 wget && \
        pip install -q torch==2.0.1+cu118 torchvision==0.15.2+cu118 torchaudio==2.0.2+cu118 torchtext==0.15.2 torchdata==0.6.1 --extra-index-url https://download.pytorch.org/whl/cu118 && \
        pip install -q xformers==0.0.20 triton==2.0.0 packaging==23.1"
    ),
    network_file_systems={"/content/stable-diffusion-webui": volume},
    gpu="T4",
    timeout=60000,
)
async def run():
    os.system(f"git clone https://github.com/Silversith/ComfyUI")
    os.chdir(f"/content/ComfyUI")
    os.system(f"pip install xformers -r requirements.txt")
    os.chdir(f"/content/ComfyUI")
    os.system(f"git clone https://github.com/Silversith/ComfyUI-Impact-Pack.git")
    os.chdir(f"/content/ComfyUI/custom_nodes/ComfyUI-Impact-Pack")
    os.system(f"python install.py")
    os.chdir(f"/content/ComfyUI")
    os.system(f"git -C /content/ComfyUI/custom_nodes clone https://github.com/WASasquatch/was-node-suite-comfyui/")
    os.system(f"aria2c --conditional-get --console-log-level=error -c -x 16 -s 16 -k 1M https://civitai.com/api/download/models/127297 -d /content/ComfyUI/models/checkpoints/ --auto-file-renaming=false -o htPhotorealismV417_v417SD15.safetensors")
    os.system(f"aria2c --conditional-get --console-log-level=error -c -x 16 -s 16 -k 1M https://civitai.com/api/download/models/86437 -d /content/ComfyUI/models/checkpoints/ --auto-file-renaming=false -o absolutereality_v10.safetensors")
    os.system(f"python main.py --dont-print-server")
    sys.path.append('/content/ComfyUI')
    from modules import launch_utils
    launch_utils.startup_timer.record("initial startup")
    launch_utils.prepare_environment()
    launch_utils.start()

@stub.local_entrypoint()
def main():
    run.remote()
