from fastapi import FastAPI
from pydantic import BaseModel
from compliance_env.env import ComplianceAuditorEnvironment

app = FastAPI()
env = ComplianceAuditorEnvironment()

class ResetRequest(BaseModel):
    task_id: str

@app.post("/reset")
def reset(req: ResetRequest):
    obs = env.reset(req.task_id)

    return {
        "observation": {
            "task_description": obs.task_description,
            "document_text": obs.document_text,
            "step_count": obs.step_count,
            "max_steps": obs.max_steps
        },
        "info": {}
    }
