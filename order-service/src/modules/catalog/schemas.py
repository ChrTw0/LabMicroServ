from pydantic import BaseModel, Field
from typing import Optional, List
from decimal import Decimal

# --- Category Schemas ---
class CategoryBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(CategoryBase):
    is_active: Optional[bool] = None

class CategoryResponse(CategoryBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True

# --- SampleType Schemas ---
class SampleTypeBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = None

class SampleTypeCreate(SampleTypeBase):
    pass

class SampleTypeUpdate(SampleTypeBase):
    is_active: Optional[bool] = None

class SampleTypeResponse(SampleTypeBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True

# --- Test Schemas ---
class TestBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=255)
    code: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None
    category_id: int
    sample_type_id: int
    price: Decimal = Field(..., gt=0)
    cost: Optional[Decimal] = Field(None, ge=0)
    turnaround_time: Optional[str] = Field(None, max_length=100)

class TestCreate(TestBase):
    pass

class TestUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=255)
    description: Optional[str] = None
    category_id: Optional[int] = None
    sample_type_id: Optional[int] = None
    price: Optional[Decimal] = Field(None, gt=0)
    cost: Optional[Decimal] = Field(None, ge=0)
    turnaround_time: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None

class TestResponse(TestBase):
    id: int
    is_active: bool
    category: CategoryResponse
    sample_type: SampleTypeResponse

    class Config:
        orm_mode = True

class TestListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[TestResponse]