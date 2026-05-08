from __future__ import annotations

from typing import Any

try:
    from .analysis_features import build_feature_enrichment
    from .config import get_settings
except ImportError:  # pragma: no cover - supports top-level test imports
    from analysis_features import build_feature_enrichment
    from config import get_settings


def _fallback() -> dict[str, Any]:
    return {
        "sarcasm_type": "none",
        "target": "none",
        "intensity": 1,
        "explanation": "Analysis unavailable",
        "indicators": [],
    }

import json
import time
import httpx

def analyze_with_gemini(
    text: str, language: str, is_sarcastic: bool, confidence: float
) -> dict[str, Any]:
    settings = get_settings()
    if not settings.gemini_api_key:
        return build_feature_enrichment(text, confidence, is_sarcastic, language)

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={settings.gemini_api_key}"
    
    prompt = f"""
أنت خبير في تحليل اللغة العربية واللهجات المغاربية والخليجية. 
حلل النص التالي لتحديد خصائص السخرية والتهكم.
النص: "{text}"
توقع النموذج: is_sarcastic={is_sarcastic} (الثقة: {confidence:.2f}).

يجب أن تعيد كائن JSON صالح فقط يحتوي على الحقول التالية:
- "sarcasm_type": يجب أن يكون واحداً من: ["polarity_contrast", "exaggeration", "rhetorical_question", "ironic_comparison", "none"].
- "target": الكلمة أو العبارة الدقيقة من النص التي تمثل هدف السخرية (مثال: "سونيغاز"، "المدير"، "تطبيق"، أو "none" إذا لم يكن هناك هدف محدد).
- "intensity": رقم صحيح من 1 إلى 5 يمثل شدة السخرية.
- "explanation": شرح قصير باللغة العربية لسبب اعتبار النص ساخراً.
- "indicators": مصفوفة (Array) تحتوي على الكلمات أو العبارات الدقيقة من النص التي تدل على السخرية (مثل الكلمات المتناقضة، المبالغة، الإيموجي، الأسئلة الاستنكارية).

أعد JSON فقط بدون أي نص إضافي:
"""
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.1}
    }
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            with httpx.Client() as client:
                res = client.post(url, json=payload, timeout=15.0)
                res.raise_for_status()
                response_json = res.json()
                
                # Extract text from standard Gemini REST API response format
                response_text = response_json["candidates"][0]["content"]["parts"][0]["text"].strip()
            
            # Clean markdown formatting if present
            if response_text.startswith("```json"):
                response_text = response_text[7:-3].strip()
            elif response_text.startswith("```"):
                response_text = response_text[3:-3].strip()
                
            data = json.loads(response_text)
            
            # Ensure we always return valid keys
            return {
                "sarcasm_type": data.get("sarcasm_type", "none"),
                "target": data.get("target", "none"),
                "intensity": int(data.get("intensity", 1)),
                "explanation": data.get("explanation", ""),
                "indicators": data.get("indicators", [])
            }
            
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            print(f"Gemini API Connection Error (Attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(2) # Wait 2 seconds before retrying
            else:
                # If we exhausted retries, fallback
                return build_feature_enrichment(text, confidence, is_sarcastic, language)
        except Exception as e:
            # For JSON parse errors or other non-network issues, just fallback immediately
            print(f"Gemini API General Error: {e}")
            return build_feature_enrichment(text, confidence, is_sarcastic, language)
    
    return build_feature_enrichment(text, confidence, is_sarcastic, language)
