# FAQ & Architecture Guide

## Architecture Overview

### Q: What architectural pattern does this template follow?

**Clean Architecture** with **Domain-Driven Design (DDD)** principles. The codebase is organized in concentric layers where dependencies flow inward:

```
app/
├── core/                    # Domain Layer - Business Logic
│   ├── value_objects/       # Immutable domain primitives (Email, Password, ID)
│   ├── entities/            # Domain entities with business rules
│   ├── ports/               # Domain interfaces (Dependency Inversion)
│   ├── exceptions.py        # Centralized domain exceptions
│   ├── dtos/                # Data Transfer Objects
│   └── usecases/            # Application business logic
├── infra/                   # Infrastructure Layer - External Concerns
│   ├── api/                 # FastAPI web framework
│   ├── db/                  # Database (models, repositories, migrations)
│   ├── auth/                # JWT authentication
│   └── security/            # Password hashing
├── config.py                # Application configuration
└── logger.py                # Centralized logging
```

### Q: What are Value Objects and why use them?

Value objects are immutable, self-validating domain primitives that make invalid states unrepresentable:

```python
@dataclass(frozen=True)
class Email:
    value: str
    _EMAIL_PATTERN: ClassVar = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

    def __post_init__(self):
        if not re.match(self._EMAIL_PATTERN, self.value):
            raise InvalidEmailError(f"Invalid email address {self.value}")
```

Benefits:
- **Early validation**: Errors caught at construction time, not runtime
- **Type safety**: Can't pass invalid data where valid data is expected
- **Self-documenting**: Types communicate valid states

### Q: How do Entities differ from Value Objects?

- **Entities**: Have unique identity (ID), can conceptually change over time
- **Value Objects**: No identity, defined entirely by their values, immutable

```python
@dataclass(frozen=True)
class User:  # Entity
    id: ID  # Unique identity
    name: str
    email: Email  # Value object
    password: Password  # Value object
```

### Q: What are Ports and how do they work?

Ports are interfaces that define what the domain needs from infrastructure, enabling dependency inversion:

```python
class UserRepo(Protocol):
    async def save(self, user: User) -> None: ...
    async def get_by_email(self, email: Email) -> Optional[User]: ...

class UserUnitOfWork(UnitOfWork, Protocol):
    user_repo: UserRepo
```

The domain defines the interface, infrastructure implements it.

### Q: When should I use Unit of Work pattern?

Use UoW when you need to coordinate multiple repository operations in a single transaction:

```python
async with uow:
    user = await uow.user_repo.get_by_id(user_id)
    # Multiple operations...
    await uow.commit()  # All succeed or all fail
```

For single operations, use the repository directly (see `DeleteUserUsecase`).

## Implementation Details

### Q: How does authentication work?

OAuth2 + JWT implementation:

1. User submits credentials to `/auth/token` (form data, not JSON - OAuth2 spec requirement)
2. System validates and returns JWT access token
3. Protected endpoints require `Authorization: Bearer <token>` header

**Important**: OAuth2 requires `username` field even when using email:

```javascript
const formData = new URLSearchParams();
formData.append('username', email);  // Email goes in 'username' field
formData.append('password', password);
```

### Q: How is error handling structured?

Domain exceptions are caught and transformed to HTTP responses in the API layer:

```python
@router.post("", status_code=201)
async def create(dto: CreateUserRequest, usecase: CreateUserUsecase) -> UserResponse:
    try:
        return await usecase.execute(dto)
    except (InvalidUserError, InvalidEmailError) as e:
        raise HTTPException(400, detail=str(e))
    except UserAlreadyExistsError:
        raise HTTPException(409, detail="User already exists")
```

### Q: What's the testing strategy?

- **Unit Tests**: Use `MagicMock` and `AsyncMock` to test domain logic in isolation
- **Integration Tests**: Test full stack with real database
- **Coverage**: All layers have appropriate test coverage

```python
@pytest.fixture
def mock_user_repo():
    repo = MagicMock()
    repo.save = AsyncMock()
    repo.get_by_email = AsyncMock(return_value=None)
    return repo
```

### Q: Why use SQLModel with Alembic?

- **SQLModel**: Type-safe ORM that integrates with Pydantic and FastAPI
- **Alembic**: Robust migration system for schema evolution
- **PostgreSQL**: Production-ready database with ACID compliance

## Development Workflow

### Q: How do I add a new feature?

1. **Define value objects** for new domain concepts
2. **Create/update entities** with business rules
3. **Add ports** for external dependencies
4. **Implement use cases** for business operations
5. **Add infrastructure** (repositories, API endpoints)
6. **Write tests** at appropriate layers

### Q: How does dependency injection work?

FastAPI's `Depends` system manages dependencies:

```python
CreateUserUsecase = Annotated[
    CreateUserUsecaseClass,
    Depends(
        lambda uow=Depends(get_user_uow), hasher=Depends(get_hasher):
        CreateUserUsecaseClass(uow, hasher)
    )
]
```

### Q: What are pre-commit hooks?

Automated code quality checks before each commit:
- Formatting with Ruff
- Type checking with MyPy
- File validation (YAML, JSON, TOML)

Install with `make pre-commit-install`, bypass with `git commit --no-verify` when needed.

### Q: How is configuration managed?

Pydantic Settings provides type-safe configuration with validation:

```python
class Settings(BaseSettings):
    ENV: Literal["test", "dev", "prod"] = "dev"
    DB_URL: str  # Required, validated
    JWT_SECRET_KEY: str

    model_config = SettingsConfigDict(env_file=".env")
```

## Common Issues

### Q: Why does `/auth/token` require form data instead of JSON?

OAuth2 specification mandates form-encoded data for the password flow. This ensures compatibility with OAuth2 tools and clients.

### Q: How do I handle validation errors in API endpoints?

Catch value object exceptions and transform them to appropriate HTTP responses. See error handling example above.

### Q: When should I create a new value object?

When you have:
- Domain concepts with validation rules
- Data that should be immutable
- Primitives that appear together frequently (e.g., Money with amount and currency)

This architecture ensures separation of concerns, type safety, and maintainability while keeping business logic pure and testable.
