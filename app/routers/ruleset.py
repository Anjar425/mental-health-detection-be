from fastapi import APIRouter, Depends
from ..schemas import RuleResponseSchema, RuleCreateOrUpdate
from ..controllers import RulesetController

router = APIRouter()

@router.get("/", response_model=list[RuleResponseSchema])
def get_all_rules(current_user=Depends(RulesetController().get_current_user)):
    rules = RulesetController().get_user_rules(current_user=current_user)
    
    return rules

@router.post("/")
def create_rule(data: RuleCreateOrUpdate, current_user=Depends(RulesetController().get_current_user)):
    rules = RulesetController().create_and_edit_rule(data=data, current_user=current_user)
    
    return rules
