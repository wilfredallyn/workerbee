import json

from ai_worker.main import WorkerMain, Config
from gguf_loader.main import download_gguf, main as loader_main, get_size

try:
    from pynvml.smi import nvidia_smi
except ImportError:
    nvidia_smi = None


def test_conn_str():
    msg = WorkerMain.connect_message()
    js = json.loads(msg)

    if nvidia_smi:
        assert js["nv_driver_version"]
        assert js["nv_gpu_count"]

    assert js["cpu_count"]
    assert js["vram"]


async def test_wm():
    wm = WorkerMain(Config())
    await wm.load_model("TheBloke/WizardLM-7B-uncensored-GGML:q4_K_M")
    res = wm.llama_cli.post("/v1/chat/completions", json=dict(
        model=wm.llama_model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": "hello"},
        ]
    ))
    assert res

def test_download_model():
    assert get_size("TheBloke/WizardLM-7B-uncensored-GGML:q4_K_M") > 0
    assert download_gguf("TheBloke/WizardLM-7B-uncensored-GGML:q4_K_M")


def test_download_main(capsys):
    loader_main(["TheBloke/WizardLM-7B-uncensored-GGML:q4_K_M"])
    oe = capsys.readouterr().out
    assert "q4_K_M" in oe