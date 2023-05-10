from fastapi import APIRouter
from tortoise.contrib.fastapi import HTTPNotFoundError

from .models import MarketData, MarketData_Pydantic
from .schemas import MarketDataCreate

router = APIRouter()


@router.post("/market_data", response_model=MarketData_Pydantic)
async def upload_market_data(option: MarketDataCreate) -> MarketData_Pydantic:
    option_dict = option.dict()
    obj = await MarketData.create(**option_dict)
    return MarketData_Pydantic.from_orm(obj)

# @router.post("/market_data", response_model=MarketData_Pydantic)
# async def upload_market_data(option: MarketDataCreate) -> MarketData_Pydantic:
#     obj = await MarketData.create(**option.dict())
#     return MarketData_Pydantic.from_orm(obj)


@router.get("/market_data", response_model=list[MarketData_Pydantic])
async def get_all_market_data() -> list[MarketData_Pydantic]:
    data = await MarketData_Pydantic.from_queryset(MarketData.all())
    return data


@router.get(
    "/market_data/{option_id}",
    response_model=MarketData_Pydantic,
    responses={404: {"model": HTTPNotFoundError}},
)
async def get_market_data(option_id: int) -> MarketData_Pydantic:
    return await MarketData_Pydantic.from_queryset_single(MarketData.get(id=option_id))
