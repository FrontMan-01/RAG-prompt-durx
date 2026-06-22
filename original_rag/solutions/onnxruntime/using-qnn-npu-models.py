
""" Example of using QNN Onnxruntime Models on Windows Arm64 

    -- NPU optimized models for Windows ARM64 with Qualcomm Snapdragon NPU
    -- tested on both X1 and X2

    To use, pip install the following (pinned to specific versions):

    --pip3 install onnxruntime-qnn==2.1.0
    --pip3 install onnxruntime-genai==0.13.2
    --pip3 install onnxruntime-core==1.25+

    Note: this aligns to the latest QNN library 2.45 (May 2026)

    If you can not use this combination, then we recommend fallback to:

    --pip3 install onnxruntime-qnn==1.22.2
    --pip3 install onnxruntime-genai==0.9.0

    Note: this aligns to QNN SDK 2.36.1, and is similar to Windows FoundryLocal

    To use onnxruntime with qnn backend provider, the backend must be registered, which
    requires an absolute file path to a backend providers_qnn dll library - this is handled by
    default in llmware.

    If you have a custom install of onnxruntime-qnn, then you can set an environment variable to
    that path, e.g.,

    os.environ["qnn_onnx_path"] = "C:\\path\\to\\onnxruntime_providers_qnn.dll"

    Generally, you can find this .dll in the onnxruntime-qnn folder path

    """


from llmware.models import ModelCatalog

# qnn models in llmware model catalog

qnn_model_list = ["llama-3.2-3b-onnx-qnn",
                  "phi-3.5-mini-instruct-onnx-qnn",
                  "phi-3-mini-4k-instruct-onnx-qnn",
                  "qwen2.5-1.5b-instruct-onnx-qnn",
                  "qwen2.5-7b-instruct-onnx-qnn",
                  "deepseek-r1-distill-qwen-7b-onnx-qnn",
                  "deepseek-r1-distill-qwen-14b-onnx-qnn"
                  ]

# select a model
qnn_model_name = qnn_model_list[1]

# load model
qnn_model = ModelCatalog().load_model(qnn_model_name, max_output=200)

prompt = "Write a 100 word essay on the major themes of Moby Dick."

# run stream with prompt
for token in qnn_model.stream(prompt):
    print(token, end="")



