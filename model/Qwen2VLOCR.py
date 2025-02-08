import warnings

import PIL.Image
import torch
from qwen_vl_utils import process_vision_info
from transformers import Qwen2VLForConditionalGeneration, AutoProcessor, BitsAndBytesConfig

from model.BaseModel import BaseModel


class Qwen2VLOCR(BaseModel):
    def __init__(self, load_in_8bit=False, load_in_4bit=False):
        super().__init__()
        self.load_in_4bit = load_in_4bit
        self.load_in_8bit = load_in_8bit
        self.processor = None
        self.model = None

    def load(self):
        use_flash_attn_2 = False
        try:
            import flash_attn
            use_flash_attn_2 = True
        except ImportError as e:
            warnings.warn('flash attention 2 not supported, fall back to default')

        print('start loading model')
        if self.load_in_4bit:
            model = Qwen2VLForConditionalGeneration.from_pretrained(
                "prithivMLmods/Qwen2-VL-OCR-2B-Instruct",
                device_map='auto',
                torch_dtype=torch.bfloat16,
                attn_implementation='flash_attention_2' if use_flash_attn_2 else None,
                quantization_config=BitsAndBytesConfig(
                    load_in_4bit=True
                )
            )
        elif self.load_in_8bit:
            model = Qwen2VLForConditionalGeneration.from_pretrained(
                "prithivMLmods/Qwen2-VL-OCR-2B-Instruct",
                device_map='auto',
                torch_dtype=torch.bfloat16,
                attn_implementation='flash_attention_2' if use_flash_attn_2 else None,
                quantization_config=BitsAndBytesConfig(
                    load_in_8bit=True
                )
            )
        else:
            model = Qwen2VLForConditionalGeneration.from_pretrained(
                "prithivMLmods/Qwen2-VL-OCR-2B-Instruct",
                device_map='auto',
                torch_dtype=torch.bfloat16,
                attn_implementation='flash_attention_2' if use_flash_attn_2 else None
            )
        self.model = model

        processor = AutoProcessor.from_pretrained("prithivMLmods/Qwen2-VL-OCR-2B-Instruct")
        processor.tokenizer.padding_side = 'left'
        self.processor = processor
        print('loading complete')

    def process(self, image: PIL.Image.Image) -> str:
        print('start processing')
        messages = [{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "image": image,
                },
                {"type": "text", "text": "Understand and print the latex formula only."},
            ],
        }]

        text = []
        for message in messages:
            text_ = self.processor.apply_chat_template(
                [message], tokenize=False, add_generation_prompt=True
            )
            text.append(text_)
        image_inputs, video_inputs = process_vision_info(messages)
        inputs = self.processor(
            text=text,
            images=image_inputs,
            videos=video_inputs,
            padding=True,
            return_tensors="pt",
        )

        inputs = inputs.to("cuda")

        # Inference: Generation of the output
        generated_ids = self.model.generate(**inputs, max_new_tokens=128)
        inputs = inputs.to('cpu')
        generated_ids_trimmed = [
            out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
        ]
        output_text = self.processor.batch_decode(
            generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
        )

        del generated_ids
        del inputs
        del generated_ids_trimmed

        output_text[0] = output_text[0].replace('<|im_end|>', '').replace('<|vision_pad|>', '').replace(
            '<|im_start|>user', '')

        torch.cuda.empty_cache()
        return output_text[0]
