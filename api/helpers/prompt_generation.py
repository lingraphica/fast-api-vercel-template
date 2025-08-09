from typing import List, Optional


def create_base_prompt(
    statement: str,
    objective: str,
    num_replies: int,
    complexity_level: int = 3,
    num_emojis: int = 0,
) -> str:
    prompt = (
        f"Generate exactly and ONLY {num_replies} conversational phrase or phrases responding to: {statement}   Context: User's objective is to {objective}   Guidelines:\n"
        "       - Each phrase should be natural and conversational\n"
    )
    if complexity_level == 1:
        prompt += (
            "    - Maximum 5 words per phrase\n"
            "    - Phrase should use simple words\n"
            "    - Phrase should not add extra information\n"
        )
    elif complexity_level == 2:
        prompt += (
            "   - Maximum 8 words per phrase\n"
            "   - Phrase should use common words\n"
            "   - Phrase should not add extra information\n"
        )
    else:
        prompt += " - Maximum 10 words per phrase\n"
    prompt += (
        " - Vary the structure and starting words\n"
        "       - Phrases should directly address the previous statement\n"
        "       - Avoid generic responses like  - That's interesting - unless truly appropriate\n"
        " Return ONLY a valid JSON object with the structure with key as 'suggestions'\n"
        " The JSON format should be strictly like - \n"
        " suggestions: [\n"
        "  {\n"
        "    id: <number>,\n"
        "    text: <string>,\n"
    )
    if num_emojis > 0:
        prompt += "    emoji: <string>\n"
    prompt += (
        "  }\n"
        " ]"
        "   Do not include any extra formatting\n"
        f"   ASSURE EXACTLY {num_replies} suggestions\n"
        f"   Make sure the response contains EXACTLY {num_replies} suggestions\n"
    )
    return prompt


def create_prompt(
    statement: str,
    objective: str,
    num_replies: int,
    mood: Optional[str] = None,
    complexity_level: int = 3,
    previous_suggestions: Optional[List[str]] = None,
    context: Optional[List[str]] = None,
    num_emojis: int = 0,
) -> str:
    prompt = create_base_prompt(
        statement, objective, num_replies, complexity_level, num_emojis
    )
    if mood:
        prompt += f"\nMOOD and TONE: {mood}"
        prompt += "\nHeavily consider the mood."
    if previous_suggestions:
        last_ten = previous_suggestions[-10:]
        prompt += (
            f"\nThese are previous suggestions that the user did not like: {last_ten}"
        )
        prompt += "\nGenerate unique suggestions that are SIGNIFICANTLY DIFFERENT."
    if context:
        last_ten_context = context[-10:]
        context_str = " | ".join(
            [item if isinstance(item, str) else str(item) for item in last_ten_context]
        )
        prompt += f"\nprevious chat context: {context_str}"
        prompt += "\nWeigh the users input in the context heavily."
    return prompt


def create_phrase_building_prompt(
    items: List[str], previous_attempts: Optional[List[str]] = None
) -> str:
    prompt = f"Form a single coherent message from the following: {', '.join(items)}."
    if previous_attempts and len(previous_attempts) > 0:
        prompt += f" DO NOT GENERATE messages similar to these previous attempts: {' | '.join(previous_attempts)}."
    prompt += (
        "\nAssure the response is simple, and easy to understand aphasia-friendly language. "
        " Return ONLY a valid JSON object with the structure with key as 'suggestions'\n"
        " The JSON format should be strictly like - \n"
        " { suggestions: [\n"
        "  {\n"
        "    id: <number>,\n"
        "    text: <string>,\n"
        "    emoji: <string>\n"
        "  }\n"
        " ]}"
        "   Do not include any extra formatting\n"
        "Do not include any markdown or code block formatting. return only the message, no other text. Emoji should be a string"
    )
    return prompt
