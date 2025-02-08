import torch
from qwen_vl_utils import process_vision_info
from transformers import AutoProcessor, Qwen2VLForConditionalGeneration, \
    BitsAndBytesConfig

model = Qwen2VLForConditionalGeneration.from_pretrained(
    "prithivMLmods/Qwen2-VL-OCR-2B-Instruct",
    device_map='auto',
    torch_dtype=torch.bfloat16,
    attn_implementation='flash_attention_2',
    # quantization_config=BitsAndBytesConfig(
    #     load_in_8bit=True
    # )
)

# default processer
processor = AutoProcessor.from_pretrained("prithivMLmods/Qwen2-VL-OCR-2B-Instruct")
processor.tokenizer.padding_side = 'left'
# load dataset
from datasets import load_dataset

test_dataset = load_dataset("linxy/LaTeX_OCR", name="full", split="test")

tot_output = []

from tqdm import tqdm

batch = 16
n = len(test_dataset)
proc = tqdm(range(0, n, batch))
for i in proc:
    data = test_dataset[i:i + batch]
    messages = []
    for j in range(len(data['image'])):
        message = {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "image": data['image'][j],
                },
                {"type": "text", "text": "Understand and print the latex formula only."},
            ],
        }
        messages.append(message)

    # Preparation for inference
    text = []
    for message in messages:
        text_ = processor.apply_chat_template(
            [message], tokenize=False, add_generation_prompt=True
        )
        text.append(text_)
    image_inputs, video_inputs = process_vision_info(messages)
    inputs = processor(
        text=text,
        images=image_inputs,
        videos=video_inputs,
        padding=True,
        return_tensors="pt",
    )

    inputs = inputs.to("cuda")

    # Inference: Generation of the output
    generated_ids = model.generate(**inputs, max_new_tokens=2048)
    inputs = inputs.to('cpu')
    generated_ids_trimmed = [
        out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
    ]
    output_text = processor.batch_decode(
        generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
    )

    del generated_ids
    del inputs
    del generated_ids_trimmed

    for i in range(len(output_text)):
        output_text[i] = output_text[i].replace('<|im_end|>', '').replace('<|vision_pad|>', '').replace(
            '<|im_start|>user', '')
    tot_output.extend(output_text)
    proc.set_postfix_str(f'{len(tot_output)}')
    torch.cuda.empty_cache()

tot_ref = []
tot_ref.extend(test_dataset[:len(tot_output)]['text'])

import pickle

with open('./output/output.pth', 'wb') as f:
    pickle.dump(tot_output, f)
with open('./output/ref.pth', 'wb') as f:
    pickle.dump(tot_ref, f)

# print(output_text[0])
# print(test_dataset[2]['text'])
