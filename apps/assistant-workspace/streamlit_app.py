from __future__ import annotations
from datetime import datetime, timezone
import streamlit as st

st.set_page_config(page_title="Assistant Workspace", layout="wide")
NAV_ITEMS=["Assistant Home","Plan Builder","Workflow Studio","Skill Library","Knowledge Base","Task & Schedule Center"]

def _init_state()->None:
    if "workspace" not in st.session_state:
        now=datetime.now(timezone.utc).isoformat()
        st.session_state.workspace={"active_nav":NAV_ITEMS[0],"context":{"session_id":datetime.now(timezone.utc).strftime("WS-%Y%m%d-%H%M%S"),"goal":"","last_action":"initialized","updated_at":now},"panels":{"conversation":[],"plan":[{"step":"Define objective","status":"pending"},{"step":"Draft execution plan","status":"pending"}],"artifacts":[],"knowledge":[]}}

def _sync_action(user_text:str)->None:
    ws=st.session_state.workspace; now=datetime.now(timezone.utc).isoformat()
    ws["panels"]["conversation"] += [{"role":"user","text":user_text,"at":now},{"role":"assistant","text":f"Captured request: {user_text}. Plan/artifacts/knowledge synchronized.","at":now}]
    ws["context"].update({"goal":user_text,"last_action":"chat_message","updated_at":now})
    ws["panels"]["plan"][0]["status"]="done"; ws["panels"]["plan"][1]["status"]="in_progress"; ws["panels"]["plan"].append({"step":f"Execute: {user_text}","status":"queued"})
    ws["panels"]["artifacts"].append({"name":f"plan-brief-{len(ws['panels']['artifacts'])+1}.md","type":"plan-brief","summary":f"Auto-generated plan brief for: {user_text}","at":now})
    ws["panels"]["knowledge"].append({"topic":user_text,"note":"Stored as reusable context memory from conversation.","at":now})

def main()->None:
    _init_state(); ws=st.session_state.workspace
    st.sidebar.title("Workspace Navigation")
    ws["active_nav"]=st.sidebar.radio("Surface",NAV_ITEMS,index=NAV_ITEMS.index(ws["active_nav"]))
    st.sidebar.caption(f"Session: {ws['context']['session_id']}")
    st.title("Assistant Workspace"); st.caption("Primary app surface for shared session context across chat, planning, artifacts, and memory.")
    st.info(f"Active surface: **{ws['active_nav']}**")
    c1,c2,c3,c4=st.columns([2,1.2,1.2,1.2])
    with c1:
        st.subheader("Conversation")
        msg=st.text_input("Send a message",placeholder="Describe your goal…")
        if st.button("Sync from chat",use_container_width=True) and msg.strip(): _sync_action(msg.strip())
        for row in reversed(ws["panels"]["conversation"][-8:]): st.markdown(f"**{row['role']}**: {row['text']}")
    with c2:
        st.subheader("Working Plan")
        for step in ws["panels"]["plan"][-8:]: st.write(f"- {step['step']} — `{step['status']}`")
    with c3:
        st.subheader("Artifacts")
        for a in ws["panels"]["artifacts"][-8:]: st.write(f"- {a['name']} ({a['type']})"); st.caption(a["summary"])
    with c4:
        st.subheader("Knowledge / Memory")
        for k in ws["panels"]["knowledge"][-8:]: st.write(f"- {k['topic']}"); st.caption(k["note"])

if __name__=="__main__": main()
