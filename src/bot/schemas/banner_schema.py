from pydantic import ConfigDict, BaseModel, Field


class BannerSchemaRead(BaseModel):
    name: str
    image: str
    description: str

    model_config = ConfigDict(from_attributes=True)


class BannerSchemaBase(BannerSchemaRead):
    id: int
