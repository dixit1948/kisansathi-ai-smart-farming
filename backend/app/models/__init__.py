"""Models package — import all to register with Base.metadata."""
from app.models.user import User, UserRole
from app.models.farmer import FarmerProfile
from app.models.farm import Farm, Crop, FarmCrop, SoilType, IrrigationType, CropStage
from app.models.conversation import Conversation, Message, MessageRole, Channel
from app.models.scan import Scan, ScanSeverity
from app.models.alert import Alert, AlertType, AlertSeverity
from app.models.market import MarketPrice
from app.models.knowledge import KnowledgeDocument, KnowledgeChunk
from app.models.trace import AgentTrace, AuditLog, WeatherCache

__all__ = [
    "User", "UserRole",
    "FarmerProfile",
    "Farm", "Crop", "FarmCrop", "SoilType", "IrrigationType", "CropStage",
    "Conversation", "Message", "MessageRole", "Channel",
    "Scan", "ScanSeverity",
    "Alert", "AlertType", "AlertSeverity",
    "MarketPrice",
    "KnowledgeDocument", "KnowledgeChunk",
    "AgentTrace", "AuditLog", "WeatherCache",
]
