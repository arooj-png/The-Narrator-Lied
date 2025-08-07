def build_gemini_prompt(user_story):
    return f"""
Analyze this user-submitted story:

\"\"\"{user_story}\"\"\"

Do the following:
1. Detect the mood (1 word).
2. Identify the main archetype (1 phrase).
3. Predict what might happen next (1-2 lines).
4. Create a dramatic quote (1 line).
5. Suggest a soundtrack vibe (e.g. "Silence", "Haunting Piano").
6. Suggest 2 user choices in the format: ["Choice A...", "Choice B..."].
7. After a user selects one of the choices, continue the story with a brief paragraph showing what happens next.
8. Optionally include a rare "easter_egg" (1 in 10 cases), such as a mysterious item, hidden message, or secret character.

Respond ONLY in this strict JSON format:

{{
  "mood": "...",
  "archetype": "...",
  "next_line": "...",
  "truth_summary": "...",
  "soundtrack": "...",
  "choices": ["...", "..."],
  "result_of_choice": "...",
  "easter_egg": "..."
}}

⚠️ Your response MUST be valid JSON. DO NOT include markdown, explanations, or formatting outside the JSON.
"""
