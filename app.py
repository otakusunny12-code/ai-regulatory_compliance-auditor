from fastapi import FastAPI
from pydantic import BaseModel
from compliance_env.env import ComplianceAuditorEnvironment, Action

app = FastAPI()

env = ComplianceAuditorEnvironment()

class ResetRequest(BaseModel):
    task_id: str

class StepRequest(BaseModel):
    findings: list
    is_submission: bool = True


@app.post("/reset")
def reset(req: ResetRequest):
    obs = env.reset(req.task_id)
    return {
        "task_description": obs.task_description,
        "document_text": obs.document_text,
        "step_count": obs.step_count,
        "max_steps": obs.max_steps
    }


@app.post("/step")
def step(req: StepRequest):
    action = Action(findings=[], is_submission=req.is_submission)
    obs, reward, done, info = env.step(action)

    return {
        "reward": reward,
        "done": done,
        "info": info
    }
