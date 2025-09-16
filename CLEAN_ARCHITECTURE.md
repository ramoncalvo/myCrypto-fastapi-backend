# MyCrypto Clean Architecture Implementation

This document describes the clean architecture implementation for the MyCrypto FastAPI backend.

## Architecture Overview

The application follows Clean Architecture principles with clear separation of concerns across four main layers:

### 1. Domain Layer (`domain/`)
Contains the core business logic and rules. This layer is independent of any external concerns.

- **Entities**: Core business objects with behavior
  - `User` - User domain entity with profile management
  - `CryptoAsset` - Cryptocurrency asset with price management
  - `Portfolio` - Portfolio entry with profit/loss calculations

- **Value Objects**: Immutable objects that represent domain concepts
  - `UserId`, `AssetId`, `PortfolioId` - Unique identifiers
  - `Email` - Email validation and formatting
  - `Symbol` - Cryptocurrency symbol validation

### 2. Application Layer (`application/`)
Contains use cases and application-specific business rules.

- **Use Cases**: Application business rules and orchestration
  - `UserUseCases` - User management operations
  - `CryptoAssetUseCases` - Asset management operations
  - `PortfolioUseCases` - Portfolio management and calculations

- **DTOs**: Data Transfer Objects for application layer communication
  - Request/Response objects for each use case

- **Interfaces**: Abstract definitions for external dependencies
  - Repository interfaces that the infrastructure layer implements

### 3. Infrastructure Layer (`infrastructure/`)
Contains implementations of external concerns.

- **Repositories**: Database implementations
  - `MongoUserRepository` - MongoDB user data access
  - `MongoCryptoAssetRepository` - MongoDB asset data access
  - `MongoPortfolioRepository` - MongoDB portfolio data access

- **Dependency Injection**: Container for managing dependencies
  - `DIContainer` - Wires up all dependencies

### 4. Presentation Layer (`presentation/`)
Contains the web API and external interfaces.

- **API Routes**: FastAPI route handlers
  - `user_routes.py` - User endpoint handlers
  - `crypto_asset_routes.py` - Asset endpoint handlers
  - `portfolio_routes.py` - Portfolio endpoint handlers

- **Schemas**: Pydantic models for API serialization
  - Request/Response schemas for each endpoint

- **Dependencies**: FastAPI dependency injection setup

## Key Benefits

### 1. **Dependency Inversion**
- High-level modules don't depend on low-level modules
- Both depend on abstractions (interfaces)
- Easy to swap implementations (e.g., MongoDB → PostgreSQL)

### 2. **Separation of Concerns**
- Each layer has a single responsibility
- Business logic is isolated from infrastructure concerns
- Clear boundaries between layers

### 3. **Testability**
- Domain logic can be tested without external dependencies
- Use cases can be tested with mock repositories
- Each layer can be tested independently

### 4. **Maintainability**
- Changes in one layer don't affect others
- New features follow established patterns
- Code is organized by business capability

## Usage

### Running the Clean Architecture Version

```bash
# Use the new clean architecture main file
uvicorn main_clean:app --reload
```

### Key Differences from Original

1. **Domain Entities**: Rich objects with business behavior instead of anemic data models
2. **Use Cases**: Explicit application services instead of direct repository calls in routes
3. **Value Objects**: Type-safe domain concepts with validation
4. **Dependency Injection**: Proper IoC container instead of global database factory
5. **Interface Segregation**: Repository interfaces separate from implementations

### Example: Creating a User

**Before (Anemic Model)**:
```python
@app.post("/users/")
async def create_user(user: UserCreate):
    user_data = user.model_dump()
    result = await db_factory.user_repository.create(user_data)
    return result
```

**After (Rich Domain Model)**:
```python
@router.post("/users/")
async def create_user(
    user_data: UserCreateSchema,
    user_use_cases: UserUseCases = Depends(get_user_use_cases)
):
    request = CreateUserRequest(...)
    user_response = await user_use_cases.create_user(request)
    return UserResponseSchema.from_dto(user_response)
```

## Migration Strategy

1. **Gradual Migration**: Both `main.py` and `main_clean.py` can coexist
2. **Feature Parity**: All existing endpoints are preserved with same API contracts
3. **Database Compatibility**: Uses same MongoDB collections and schemas
4. **Testing**: Existing tests should work with minimal modifications

## Next Steps

1. **Update Authentication**: Migrate auth module to use clean architecture
2. **Add Domain Services**: Complex business logic that spans multiple entities
3. **Event Sourcing**: Add domain events for audit trails
4. **CQRS**: Separate read/write models for complex queries
5. **Integration Tests**: Add tests that verify the entire application flow
