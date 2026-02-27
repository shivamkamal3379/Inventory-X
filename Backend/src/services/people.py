from src.services.base import CRUDBase
from src.models.people import Agent, Party
from src.schemas.people import AgentCreate, AgentBase, PartyCreate, PartyBase

 
class CRUDAgent(CRUDBase[Agent, AgentCreate, AgentBase]):
    pass


class CRUDParty(CRUDBase[Party, PartyCreate, PartyBase]):
    pass


agent_service = CRUDAgent(Agent)
party_service = CRUDParty(Party)
