def extract_meeting_actions(transcript:str)->dict:
    return {"summary": transcript[:120], "actions": [], "decisions": []}
