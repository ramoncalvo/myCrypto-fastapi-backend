from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from application.use_cases.crypto_asset_use_cases import CryptoAssetUseCases
from application.dtos.crypto_asset_dtos import CreateCryptoAssetRequest, UpdateCryptoAssetRequest
from presentation.dependencies import get_crypto_asset_use_cases
from presentation.schemas.crypto_asset_schemas import (
    CryptoAssetCreateSchema, CryptoAssetUpdateSchema, CryptoAssetResponseSchema
)


router = APIRouter(prefix="/crypto-assets", tags=["Crypto Assets"])


@router.post("/", response_model=CryptoAssetResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_crypto_asset(
    asset_data: CryptoAssetCreateSchema,
    crypto_asset_use_cases: CryptoAssetUseCases = Depends(get_crypto_asset_use_cases)
):
    """Create a new crypto asset"""
    try:
        request = CreateCryptoAssetRequest(
            symbol=asset_data.symbol,
            name=asset_data.name,
            current_price=asset_data.current_price
        )
        
        asset_response = await crypto_asset_use_cases.create_crypto_asset(request)
        return CryptoAssetResponseSchema.from_dto(asset_response)
        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create crypto asset")


@router.get("/", response_model=List[CryptoAssetResponseSchema])
async def get_crypto_assets(
    skip: int = 0,
    limit: int = 100,
    crypto_asset_use_cases: CryptoAssetUseCases = Depends(get_crypto_asset_use_cases)
):
    """Get all crypto assets with pagination"""
    try:
        assets = await crypto_asset_use_cases.get_all_assets(skip=skip, limit=limit)
        return [CryptoAssetResponseSchema.from_dto(asset) for asset in assets]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve crypto assets")


@router.get("/{asset_id}", response_model=CryptoAssetResponseSchema)
async def get_crypto_asset(
    asset_id: str,
    crypto_asset_use_cases: CryptoAssetUseCases = Depends(get_crypto_asset_use_cases)
):
    """Get crypto asset by ID"""
    try:
        asset = await crypto_asset_use_cases.get_asset_by_id(asset_id)
        if not asset:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Crypto asset not found")
        return CryptoAssetResponseSchema.from_dto(asset)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve crypto asset")


@router.get("/symbol/{symbol}", response_model=CryptoAssetResponseSchema)
async def get_crypto_asset_by_symbol(
    symbol: str,
    crypto_asset_use_cases: CryptoAssetUseCases = Depends(get_crypto_asset_use_cases)
):
    """Get crypto asset by symbol"""
    try:
        asset = await crypto_asset_use_cases.get_asset_by_symbol(symbol)
        if not asset:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Crypto asset not found")
        return CryptoAssetResponseSchema.from_dto(asset)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve crypto asset")


@router.put("/{asset_id}", response_model=CryptoAssetResponseSchema)
async def update_crypto_asset(
    asset_id: str,
    asset_data: CryptoAssetUpdateSchema,
    crypto_asset_use_cases: CryptoAssetUseCases = Depends(get_crypto_asset_use_cases)
):
    """Update crypto asset"""
    try:
        request = UpdateCryptoAssetRequest(
            name=asset_data.name,
            current_price=asset_data.current_price
        )
        
        asset = await crypto_asset_use_cases.update_asset(asset_id, request)
        if not asset:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Crypto asset not found")
        return CryptoAssetResponseSchema.from_dto(asset)
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update crypto asset")


@router.delete("/{asset_id}")
async def delete_crypto_asset(
    asset_id: str,
    crypto_asset_use_cases: CryptoAssetUseCases = Depends(get_crypto_asset_use_cases)
):
    """Delete crypto asset"""
    try:
        success = await crypto_asset_use_cases.delete_asset(asset_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Crypto asset not found")
        return {"message": "Crypto asset deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete crypto asset")
