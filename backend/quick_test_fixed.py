"""
Quick test script with fixed .to() issue
"""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_qwen_3b_fixed():
    """Test Qwen 3B với fix .to() issue"""
    print("=== Testing Qwen 3B với Fixed .to() Issue ===")
    
    try:
        model_name = "Qwen/Qwen2.5-3B-Instruct"
        
        print("1. Setup quantization...")
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16
        )
        
        print("2. Loading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
        
        print("3. Loading model...")
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            quantization_config=bnb_config,
            device_map="auto",
            torch_dtype=torch.bfloat16,
            trust_remote_code=True,
            low_cpu_mem_usage=True
        )
        
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
            
        print("✅ Model loaded successfully!")
        
        # Memory check
        memory_gb = torch.cuda.memory_allocated() / 1024**3
        print(f"📊 GPU Memory: {memory_gb:.2f} GB")
        
        print("\n4. Testing Vietnamese generation...")
        
        # Test prompt
        prompt = """<|im_start|>system
Bạn là một trợ lý AI thông minh. Hãy trả lời bằng tiếng Việt.<|im_end|>
<|im_start|>user
Xin chào! Hãy giới thiệu bản thân bạn.<|im_end|>
<|im_start|>assistant"""

        # Tokenize - DON'T use .to() with 4-bit models
        inputs = tokenizer(prompt, return_tensors="pt")
        print("✅ Tokenization successful")
        
        # Generate
        with torch.no_grad():
            outputs = model.generate(
                inputs.input_ids,
                attention_mask=inputs.attention_mask,
                max_new_tokens=80,
                temperature=0.7,
                top_p=0.9,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id,
                eos_token_id=tokenizer.eos_token_id
            )
        
        # Decode response
        response = tokenizer.decode(
            outputs[0][inputs.input_ids.shape[1]:], 
            skip_special_tokens=True
        ).strip()
        
        print(f"✅ Response: {response}")
        
        # Final memory check
        final_memory = torch.cuda.memory_allocated() / 1024**3
        print(f"📊 Final GPU Memory: {final_memory:.2f} GB")
        
        # Test multiple generations
        print("\n5. Testing multiple generations...")
        
        questions = [
            "Bạn có thể làm gì?",
            "Hôm nay thời tiết thế nào?",
            "Viết một câu thơ ngắn"
        ]
        
        for i, question in enumerate(questions, 1):
            test_prompt = f"""<|im_start|>system
Bạn là trợ lý AI. Trả lời ngắn gọn bằng tiếng Việt.<|im_end|>
<|im_start|>user
{question}<|im_end|>
<|im_start|>assistant"""
            
            test_inputs = tokenizer(test_prompt, return_tensors="pt")
            
            with torch.no_grad():
                test_outputs = model.generate(
                    test_inputs.input_ids,
                    max_new_tokens=50,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=tokenizer.eos_token_id
                )
            
            test_response = tokenizer.decode(
                test_outputs[0][test_inputs.input_ids.shape[1]:], 
                skip_special_tokens=True
            ).strip()
            
            print(f"Q{i}: {question}")
            print(f"A{i}: {test_response}\n")
        
        # Cleanup
        del model
        del tokenizer
        torch.cuda.empty_cache()
        
        print("🎉 All tests passed! Model working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_qwen_3b_fixed()
