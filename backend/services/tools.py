TOOLS = [
    {
        "name": "save_reason",
        "description": """사용자가 자신의 감정/상태의 이유를 말했을 때 즉시 호출하세요.
예시: '배고파' → 질문 '왜 배고파?' → '밥을 못 먹어서' → save_reason('밥을 못 먹어서')
이유가 짧거나 간단해도 저장하세요. 사용자가 직접 이유를 말하지 않아도 대화에서 이유가 드러나면 저장하세요.
한 번의 응답에서 여러 이유가 나오면 가장 핵심적인 것 하나만 저장하세요.""",
        "input_schema": {
            "type": "object",
            "properties": {
                "reason": {
                    "type": "string",
                    "description": "사용자가 말한 이유 (핵심만 간결하게)"
                }
            },
            "required": ["reason"]
        }
    },
    {
        "name": "get_reasons",
        "description": "지금까지 저장된 이유 목록과 개수를 조회합니다.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
]
