print("Step 1: Importing ModelCatalog")
from llmware.models import ModelCatalog
print("Step 2: Loading model")
model = ModelCatalog().load_model("bling-phi-3.5-gguf")
print("Step 3: Model loaded successfully:", model)
output = model.inference(
    "What is prompt injection?",
    add_context="Prompt injection is an attack where malicious instructions "
                "are hidden in retrieved documents to hijack an AI system."
)
print("Step 4: Inference output:", output)
