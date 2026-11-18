from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import datetime

class SaveCartoonRequest(BaseModel):
    title: str = Field(..., min_title=1, max_length=100, description="Title of the cartoon canvas")
    canvas_json: Dict[str, Any] = Field(..., description="Fabric.js JSON state object")
    image_base64: str = Field(..., description="Base64 encoded PNG snapshot")
    user_id: Optional[str] = Field("guest", description="Owner identifier")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "My Adventure Cartoon",
                "canvas_json": {"version": "6.0.0", "objects": []},
                "image_base64": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUg...",
                "user_id": "user_123"
            }
        }

class CartoonResponse(BaseModel):
    id: str
    title: str
    image_url: str
    created_at: datetime.datetime

    class Config:
        from_attributes = True