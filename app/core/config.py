import os
from typing import Optional
from urllib.parse import urlparse

from dotenv import load_dotenv
from pydantic import AnyHttpUrl, BaseModel, Field

load_dotenv()


class Settings(BaseModel):
    app_name: str = "EduPay Backend"
    environment: str = "development"
    api_secret_key: str = Field(...)
    admin_api_key: str = Field(...)
    database_url: str = Field("sqlite:///./edupay.db")
    webhook_base_url: Optional[AnyHttpUrl] = None

    mpesa_consumer_key: Optional[str] = None
    mpesa_consumer_secret: Optional[str] = None
    mpesa_shortcode: Optional[str] = None
    mpesa_passkey: Optional[str] = None

    orange_client_id: Optional[str] = None
    orange_client_secret: Optional[str] = None
    orange_account_number: Optional[str] = None

    airtel_client_id: Optional[str] = None
    airtel_client_secret: Optional[str] = None
    airtel_account_number: Optional[str] = None

    flutterwave_secret_key: Optional[str] = None
    flutterwave_base_url: str = Field("https://api.flutterwave.com/v3")
    flutterwave_country: str = Field("CD")
    wonya_api_key: Optional[str] = None
    wonya_base_url: Optional[str] = None
    wonya_project_ref: Optional[str] = None
    wonya_default_mobilemoney: str = Field("ORANGE")
    frontend_origins: str = Field("http://localhost:3000")

    admin_1_name: str = Field("JULVIER")
    admin_1_phone: str = Field("0994477720")
    admin_1_code: str = Field("2003")
    admin_2_name: str = Field("GRACE")
    admin_2_phone: str = Field("0995030972")
    admin_2_code: str = Field("1234")

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.frontend_origins.split(",") if origin.strip()]

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            api_secret_key=os.getenv("API_SECRET_KEY", ""),
            admin_api_key=os.getenv("ADMIN_API_KEY", ""),
            database_url=os.getenv("DATABASE_URL", "sqlite:///./edupay.db"),
            webhook_base_url=os.getenv("WEBHOOK_BASE_URL"),
            mpesa_consumer_key=os.getenv("MPESA_CONSUMER_KEY"),
            mpesa_consumer_secret=os.getenv("MPESA_CONSUMER_SECRET"),
            mpesa_shortcode=os.getenv("MPESA_SHORTCODE"),
            mpesa_passkey=os.getenv("MPESA_PASSKEY"),
            orange_client_id=os.getenv("ORANGE_CLIENT_ID"),
            orange_client_secret=os.getenv("ORANGE_CLIENT_SECRET"),
            orange_account_number=os.getenv("ORANGE_ACCOUNT_NUMBER"),
            airtel_client_id=os.getenv("AIRTEL_CLIENT_ID"),
            airtel_client_secret=os.getenv("AIRTEL_CLIENT_SECRET"),
            airtel_account_number=os.getenv("AIRTEL_ACCOUNT_NUMBER"),
            flutterwave_secret_key=os.getenv("FLUTTERWAVE_SECRET_KEY"),
            flutterwave_base_url=os.getenv("FLUTTERWAVE_BASE_URL", "https://api.flutterwave.com/v3"),
            flutterwave_country=os.getenv("FLUTTERWAVE_COUNTRY", "CD"),
            wonya_api_key=os.getenv("WONYA_API_KEY"),
            wonya_base_url=os.getenv("WONYA_BASE_URL"),
            wonya_project_ref=os.getenv("WONYA_PROJECT_REF"),
            wonya_default_mobilemoney=os.getenv("WONYA_DEFAULT_MOBILEMONEY", "ORANGE"),
            frontend_origins=os.getenv("FRONTEND_ORIGINS", "http://localhost:3000"),
            admin_1_name=os.getenv("ADMIN_1_NAME", "JULVIER"),
            admin_1_phone=os.getenv("ADMIN_1_PHONE", "0994477720"),
            admin_1_code=os.getenv("ADMIN_1_CODE", "2003"),
            admin_2_name=os.getenv("ADMIN_2_NAME", "GRACE"),
            admin_2_phone=os.getenv("ADMIN_2_PHONE", "0995030972"),
            admin_2_code=os.getenv("ADMIN_2_CODE", "1234"),
        )

    @property
    def wonya_api_url(self) -> Optional[str]:
        if not self.wonya_base_url:
            return None
        if "/projet-details/" in self.wonya_base_url:
            return "https://app-api.wonyasoft.com"
        parsed = urlparse(self.wonya_base_url)
        if parsed.scheme and parsed.netloc:
            return f"{parsed.scheme}://{parsed.netloc}".rstrip("/")
        return self.wonya_base_url.rstrip("/")

    @property
    def wonya_partner_ref(self) -> Optional[str]:
        if self.wonya_project_ref:
            return self.wonya_project_ref
        if self.wonya_base_url and "/projet-details/" in self.wonya_base_url:
            return self.wonya_base_url.rstrip("/").split("/")[-1]
        return None

    @property
    def admin_users(self):
        return [
            {"name": self.admin_1_name, "phone": self.admin_1_phone, "code": self.admin_1_code},
            {"name": self.admin_2_name, "phone": self.admin_2_phone, "code": self.admin_2_code},
        ]


settings = Settings.from_env()
