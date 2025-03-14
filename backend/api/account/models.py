from pydantic import BaseModel, Field
from typing import Optional, Any, Dict
from uuid import UUID, uuid4
import datetime as dt
from pydantic import ConfigDict

class Account(BaseModel):
    model_config = ConfigDict(from_attributes=True, allow_population_by_field_name = True)  # This allows using .model_validate(orm_obj)

    account_id: UUID = Field(default_factory=uuid4)
    short_code: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = ""
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Arbitrary user-specific metadata for customizing frontend styling and preferences.",
        alias="account_metadata"
    )
    protection: Optional[str] = None
    created_at: dt.datetime = Field(default_factory=dt.datetime.now)

class AccountCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    metadata: Optional[Dict[str, Any]] = None
    email: Optional[str]
    short_code: Optional[str]
    protection: Optional[str] = None
    name: Optional[str]

class AccountUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    account_id: Optional[UUID]
    metadata: Optional[Dict[str, Any]] = None
    email: Optional[str]
    short_code: Optional[str]
    protection: Optional[str] = None
    name: Optional[str]

class AccountResponse(BaseModel):
    account: Account

class AccountConfigResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    config: Optional[Dict[str, Any]] = Field(alias="account_metadata")
    protection: Optional[str] = None

root = Account(
    account_id="a52cb27d-4b78-4062-9687-880e879913f9",
    email="suresh@leaninnovationlabs.com",
    short_code="default",
    account_metadata={
        "root": "true",
        "palette": {
            "dark": {
                "--background": "240 10% 3.9%",
                "--foreground": "0 0% 98%",
                "--card": "240 10% 3.9%",
                "--card-foreground": "0 0% 98%",
                "--popover": "240 10% 3.9%",
                "--popover-foreground": "0 0% 98%",
                "--primary": "0 0% 98%",
                "--primary-foreground": "240 5.9% 10%",
                "--secondary": "240 3.7% 15.9%",
                "--secondary-foreground": "0 0% 98%",
                "--muted": "240 3.7% 15.9%",
                "--muted-foreground": "240 5% 64.9%",
                "--accent": "240 3.7% 15.9%",
                "--accent-foreground": "0 0% 98%",
                "--destructive": "0 62.8% 30.6%",
                "--destructive-foreground": "0 0% 98%",
                "--border": "240 3.7% 15.9%",
                "--input": "240 3.7% 15.9%",
                "--ring": "240 4.9% 83.9%"
            },
            "root": {
                "--background": "0 0% 100%",
                "--foreground": "240 10% 3.9%",
                "--card": "0 0% 100%",
                "--card-foreground": "240 10% 3.9%",
                "--popover": "0 0% 100%",
                "--popover-foreground": "240 10% 3.9%",
                "--primary": "240 5.9% 10%",
                "--primary-foreground": "0 0% 98%",
                "--secondary": "240 4.8% 95.9%",
                "--secondary-foreground": "240 5.9% 10%",
                "--muted": "240 4.8% 95.9%",
                "--muted-foreground": "240 3.8% 46.1%",
                "--accent": "240 4.8% 95.9%",
                "--accent-foreground": "240 5.9% 10%",
                "--destructive": "0 84.2% 60.2%",
                "--destructive-foreground": "0 0% 98%",
                "--border": "240 5.9% 90%",
                "--input": "240 5.9% 90%",
                "--ring": "240 10% 3.9%",
                "--radius": "0.5rem"
            }
        }
        
    },
    created_at="2024-09-12T22:10:09.211112"
)
    