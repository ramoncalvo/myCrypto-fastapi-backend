# MyCrypto API - Bitácora de Migración a Go

## 📋 Resumen del Proyecto

Esta bitácora documenta el proceso completo para recrear la API REST de MyCrypto desarrollada en FastAPI/Python utilizando Go. El proyecto original implementa una arquitectura limpia con autenticación JWT, gestión de portafolios de criptomonedas e integración con Bitso API.

## 🏗️ Arquitectura del Proyecto Original

### Estructura de Directorios (Python/FastAPI)
```
pyBackend/
├── application/           # Capa de Aplicación
│   ├── dtos/             # Data Transfer Objects
│   ├── interfaces/       # Interfaces de repositorios
│   └── use_cases/        # Casos de uso de negocio
├── domain/               # Capa de Dominio
│   ├── entities/         # Entidades de negocio
│   └── value_objects/    # Objetos de valor
├── infrastructure/       # Capa de Infraestructura
│   ├── repositories/     # Implementaciones MongoDB
│   └── services/         # Servicios externos (JWT)
├── presentation/         # Capa de Presentación
│   ├── api/             # Rutas FastAPI
│   └── schemas/         # Esquemas Pydantic
├── integrations/         # Integraciones externas
│   └── bitso/           # Cliente Bitso API
└── trading/             # Servicios de trading
```

### Arquitectura Propuesta para Go
```
go-mycrypto/
├── cmd/                  # Punto de entrada de la aplicación
│   └── server/
├── internal/             # Código interno de la aplicación
│   ├── application/      # Capa de Aplicación
│   │   ├── dto/         # Data Transfer Objects
│   │   ├── interfaces/  # Interfaces
│   │   └── usecases/    # Casos de uso
│   ├── domain/          # Capa de Dominio
│   │   ├── entities/    # Entidades
│   │   └── valueobjects/ # Objetos de valor
│   ├── infrastructure/  # Capa de Infraestructura
│   │   ├── database/    # MongoDB driver
│   │   ├── jwt/         # JWT service
│   │   └── repositories/ # Implementaciones
│   ├── presentation/    # Capa de Presentación
│   │   ├── handlers/    # HTTP handlers (Gin/Fiber)
│   │   ├── middleware/  # Middlewares
│   │   └── routes/      # Definición de rutas
│   └── integrations/    # Integraciones externas
│       └── bitso/       # Cliente Bitso
├── pkg/                 # Código reutilizable
├── configs/             # Configuraciones
├── docs/                # Documentación
└── scripts/             # Scripts de deployment
```

## 🚀 Evolución del Proyecto (Basada en Commits)

### Fase 1: Fundación (Commits: 6103a7e - c773fe1)
**Commit:** `6103a7e - Initial FastAPI v2.0 implementation`
**Equivalente en Go:**

1. **Setup inicial del proyecto Go**
```bash
go mod init github.com/username/go-mycrypto
```

2. **Dependencias principales**
```go
// go.mod
require (
    github.com/gin-gonic/gin v1.9.1          // Web framework
    github.com/golang-jwt/jwt/v5 v5.0.0      // JWT
    go.mongodb.org/mongo-driver v1.12.1      // MongoDB
    github.com/go-playground/validator/v10    // Validación
    github.com/joho/godotenv v1.4.0          // Variables de entorno
    golang.org/x/crypto v0.14.0              // Bcrypt
)
```

3. **Estructura básica de entidades**
```go
// internal/domain/entities/user.go
type User struct {
    ID           primitive.ObjectID `bson:"_id,omitempty" json:"id"`
    Email        string            `bson:"email" json:"email" validate:"required,email"`
    PasswordHash string            `bson:"password_hash" json:"-"`
    CreatedAt    time.Time         `bson:"created_at" json:"created_at"`
    UpdatedAt    time.Time         `bson:"updated_at" json:"updated_at"`
}

// internal/domain/entities/crypto_asset.go
type CryptoAsset struct {
    ID          primitive.ObjectID `bson:"_id,omitempty" json:"id"`
    Symbol      string            `bson:"symbol" json:"symbol" validate:"required"`
    Name        string            `bson:"name" json:"name" validate:"required"`
    CurrentPrice float64          `bson:"current_price" json:"current_price"`
    CreatedAt   time.Time         `bson:"created_at" json:"created_at"`
}
```

### Fase 2: Arquitectura Database-Agnostic (Commit: c773fe1)
**Commit:** `c773fe1 - FastAPI v2.0 - Database Agnostic Architecture`

1. **Interfaces de repositorio**
```go
// internal/application/interfaces/user_repository.go
type UserRepository interface {
    Create(ctx context.Context, user *entities.User) error
    GetByEmail(ctx context.Context, email string) (*entities.User, error)
    GetByID(ctx context.Context, id string) (*entities.User, error)
    Update(ctx context.Context, user *entities.User) error
    Delete(ctx context.Context, id string) error
}

// internal/application/interfaces/crypto_asset_repository.go
type CryptoAssetRepository interface {
    Create(ctx context.Context, asset *entities.CryptoAsset) error
    GetAll(ctx context.Context) ([]*entities.CryptoAsset, error)
    GetBySymbol(ctx context.Context, symbol string) (*entities.CryptoAsset, error)
    Update(ctx context.Context, asset *entities.CryptoAsset) error
}
```

2. **Implementación MongoDB**
```go
// internal/infrastructure/repositories/mongo_user_repository.go
type MongoUserRepository struct {
    collection *mongo.Collection
}

func (r *MongoUserRepository) Create(ctx context.Context, user *entities.User) error {
    user.CreatedAt = time.Now()
    user.UpdatedAt = time.Now()
    
    result, err := r.collection.InsertOne(ctx, user)
    if err != nil {
        return err
    }
    
    user.ID = result.InsertedID.(primitive.ObjectID)
    return nil
}
```

### Fase 3: Testing Suite (Commit: 2caf23d)
**Commit:** `2caf23d - Add comprehensive API testing suite`

1. **Testing framework en Go**
```go
// tests/integration/user_test.go
func TestUserEndpoints(t *testing.T) {
    // Setup test database
    testDB := setupTestDB()
    defer cleanupTestDB(testDB)
    
    // Setup test server
    router := setupTestRouter(testDB)
    
    t.Run("POST /auth/register", func(t *testing.T) {
        payload := map[string]string{
            "email":    "test@example.com",
            "password": "password123",
        }
        
        body, _ := json.Marshal(payload)
        req := httptest.NewRequest("POST", "/auth/register", bytes.NewBuffer(body))
        req.Header.Set("Content-Type", "application/json")
        
        w := httptest.NewRecorder()
        router.ServeHTTP(w, req)
        
        assert.Equal(t, http.StatusCreated, w.Code)
    })
}
```

2. **Docker setup para testing**
```dockerfile
# Dockerfile.test
FROM golang:1.21-alpine AS test
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN go test ./tests/... -v
```

### Fase 4: Docker Compose Setup (Commit: bb6635f)
**Commit:** `bb6635f - Add complete Docker Compose setup`

1. **docker-compose.yml para Go**
```yaml
version: '3.8'
services:
  api:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8080:8080"
    environment:
      - MONGODB_URI=mongodb://mongodb:27017/mycrypto
      - JWT_SECRET=${JWT_SECRET}
    depends_on:
      - mongodb
    
  mongodb:
    image: mongo:7.0
    ports:
      - "27017:27017"
    environment:
      - MONGO_INITDB_DATABASE=mycrypto
    volumes:
      - mongodb_data:/data/db
      
volumes:
  mongodb_data:
```

2. **Dockerfile para Go**
```dockerfile
FROM golang:1.21-alpine AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o main cmd/server/main.go

FROM alpine:latest
RUN apk --no-cache add ca-certificates
WORKDIR /root/
COPY --from=builder /app/main .
EXPOSE 8080
CMD ["./main"]
```

### Fase 5: JWT Authentication (Commit: 390a5ec)
**Commit:** `390a5ec - feat: implement JWT authentication module`

1. **JWT Service en Go**
```go
// internal/infrastructure/jwt/service.go
type JWTService struct {
    secretKey []byte
}

func (j *JWTService) GenerateToken(userID string) (string, error) {
    claims := jwt.MapClaims{
        "user_id": userID,
        "exp":     time.Now().Add(time.Hour * 24).Unix(),
        "iat":     time.Now().Unix(),
    }
    
    token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
    return token.SignedString(j.secretKey)
}

func (j *JWTService) ValidateToken(tokenString string) (*jwt.Token, error) {
    return jwt.Parse(tokenString, func(token *jwt.Token) (interface{}, error) {
        if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
            return nil, fmt.Errorf("unexpected signing method: %v", token.Header["alg"])
        }
        return j.secretKey, nil
    })
}
```

2. **Middleware de autenticación**
```go
// internal/presentation/middleware/auth.go
func AuthMiddleware(jwtService *jwt.JWTService) gin.HandlerFunc {
    return func(c *gin.Context) {
        authHeader := c.GetHeader("Authorization")
        if authHeader == "" {
            c.JSON(http.StatusUnauthorized, gin.H{"error": "Authorization header required"})
            c.Abort()
            return
        }
        
        tokenString := strings.Replace(authHeader, "Bearer ", "", 1)
        token, err := jwtService.ValidateToken(tokenString)
        if err != nil || !token.Valid {
            c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid token"})
            c.Abort()
            return
        }
        
        claims := token.Claims.(jwt.MapClaims)
        c.Set("user_id", claims["user_id"])
        c.Next()
    }
}
```

### Fase 6: Clean Architecture (Commit: 20f3b9b)
**Commit:** `20f3b9b - feat: implement clean architecture`

1. **Use Cases en Go**
```go
// internal/application/usecases/auth_usecase.go
type AuthUseCase struct {
    userRepo   interfaces.UserRepository
    jwtService *jwt.JWTService
}

func (uc *AuthUseCase) Register(ctx context.Context, req *dto.RegisterRequest) (*dto.AuthResponse, error) {
    // Validar si el usuario ya existe
    existingUser, _ := uc.userRepo.GetByEmail(ctx, req.Email)
    if existingUser != nil {
        return nil, errors.New("user already exists")
    }
    
    // Hash password
    hashedPassword, err := bcrypt.GenerateFromPassword([]byte(req.Password), bcrypt.DefaultCost)
    if err != nil {
        return nil, err
    }
    
    // Crear usuario
    user := &entities.User{
        Email:        req.Email,
        PasswordHash: string(hashedPassword),
    }
    
    err = uc.userRepo.Create(ctx, user)
    if err != nil {
        return nil, err
    }
    
    // Generar token
    token, err := uc.jwtService.GenerateToken(user.ID.Hex())
    if err != nil {
        return nil, err
    }
    
    return &dto.AuthResponse{
        Token: token,
        User:  user,
    }, nil
}
```

2. **DTOs en Go**
```go
// internal/application/dto/auth_dto.go
type RegisterRequest struct {
    Email    string `json:"email" validate:"required,email"`
    Password string `json:"password" validate:"required,min=8"`
}

type LoginRequest struct {
    Email    string `json:"email" validate:"required,email"`
    Password string `json:"password" validate:"required"`
}

type AuthResponse struct {
    Token string          `json:"token"`
    User  *entities.User  `json:"user"`
}
```

### Fase 7: Portfolio & Transactions (Commit: f91a828)
**Commit:** `f91a828 - feat: Fix authentication issues in portfolio and transaction endpoints`

1. **Entidades de Portfolio**
```go
// internal/domain/entities/portfolio.go
type Portfolio struct {
    ID          primitive.ObjectID `bson:"_id,omitempty" json:"id"`
    UserID      primitive.ObjectID `bson:"user_id" json:"user_id"`
    Name        string            `bson:"name" json:"name" validate:"required"`
    Description string            `bson:"description" json:"description"`
    Holdings    []Holding         `bson:"holdings" json:"holdings"`
    CreatedAt   time.Time         `bson:"created_at" json:"created_at"`
    UpdatedAt   time.Time         `bson:"updated_at" json:"updated_at"`
}

type Holding struct {
    AssetID  primitive.ObjectID `bson:"asset_id" json:"asset_id"`
    Symbol   string            `bson:"symbol" json:"symbol"`
    Quantity float64           `bson:"quantity" json:"quantity"`
    AvgPrice float64           `bson:"avg_price" json:"avg_price"`
}
```

2. **Transaction Entity**
```go
// internal/domain/entities/transaction.go
type Transaction struct {
    ID          primitive.ObjectID `bson:"_id,omitempty" json:"id"`
    UserID      primitive.ObjectID `bson:"user_id" json:"user_id"`
    PortfolioID primitive.ObjectID `bson:"portfolio_id" json:"portfolio_id"`
    AssetID     primitive.ObjectID `bson:"asset_id" json:"asset_id"`
    Type        TransactionType   `bson:"type" json:"type"`
    Quantity    float64          `bson:"quantity" json:"quantity"`
    Price       float64          `bson:"price" json:"price"`
    Status      TransactionStatus `bson:"status" json:"status"`
    CreatedAt   time.Time        `bson:"created_at" json:"created_at"`
}

type TransactionType string
const (
    TransactionTypeBuy  TransactionType = "buy"
    TransactionTypeSell TransactionType = "sell"
)

type TransactionStatus string
const (
    TransactionStatusPending   TransactionStatus = "pending"
    TransactionStatusExecuted  TransactionStatus = "executed"
    TransactionStatusCancelled TransactionStatus = "cancelled"
)
```

### Fase 8: Bitso API Integration (Implementado recientemente)

1. **Cliente Bitso en Go**
```go
// internal/integrations/bitso/client.go
type Client struct {
    httpClient *http.Client
    baseURL    string
    apiKey     string
    apiSecret  string
    rateLimiter *rate.Limiter
}

func (c *Client) GetAvailableBooks(ctx context.Context) (*BooksResponse, error) {
    req, err := http.NewRequestWithContext(ctx, "GET", c.baseURL+"/available_books", nil)
    if err != nil {
        return nil, err
    }
    
    resp, err := c.httpClient.Do(req)
    if err != nil {
        return nil, err
    }
    defer resp.Body.Close()
    
    var result BooksResponse
    err = json.NewDecoder(resp.Body).Decode(&result)
    return &result, err
}

func (c *Client) GetTicker(ctx context.Context, book string) (*TickerResponse, error) {
    // Implementación similar con rate limiting
    c.rateLimiter.Wait(ctx)
    
    url := fmt.Sprintf("%s/ticker?book=%s", c.baseURL, book)
    req, err := http.NewRequestWithContext(ctx, "GET", url, nil)
    if err != nil {
        return nil, err
    }
    
    // Agregar autenticación HMAC para endpoints privados
    if c.apiKey != "" {
        c.signRequest(req)
    }
    
    resp, err := c.httpClient.Do(req)
    if err != nil {
        return nil, err
    }
    defer resp.Body.Close()
    
    var result TickerResponse
    err = json.NewDecoder(resp.Body).Decode(&result)
    return &result, err
}
```

2. **Modelos Bitso**
```go
// internal/integrations/bitso/models.go
type Book struct {
    Book         string  `json:"book"`
    MinimumPrice string  `json:"minimum_price"`
    MaximumPrice string  `json:"maximum_price"`
    MinimumValue string  `json:"minimum_value"`
    MaximumValue string  `json:"maximum_value"`
}

type BooksResponse struct {
    Success bool   `json:"success"`
    Payload []Book `json:"payload"`
}

type Ticker struct {
    Book      string `json:"book"`
    Volume    string `json:"volume"`
    High      string `json:"high"`
    Last      string `json:"last"`
    Low       string `json:"low"`
    Vwap      string `json:"vwap"`
    Ask       string `json:"ask"`
    Bid       string `json:"bid"`
    CreatedAt string `json:"created_at"`
}
```

## 📚 Stack Tecnológico Recomendado para Go

### Core Framework
- **Gin Gonic** o **Fiber**: Web framework (equivalente a FastAPI)
- **GORM** o **MongoDB Driver**: ORM/Database driver
- **Validator**: Validación de datos (equivalente a Pydantic)

### Autenticación y Seguridad
- **golang-jwt/jwt**: JWT tokens
- **golang.org/x/crypto**: Bcrypt para passwords
- **golang.org/x/time/rate**: Rate limiting

### Base de Datos
- **go.mongodb.org/mongo-driver**: Driver oficial de MongoDB
- **testcontainers-go**: Para testing con containers

### Testing
- **testify**: Assertions y mocking
- **httptest**: Testing de HTTP handlers
- **gomock**: Generación de mocks

### Utilidades
- **godotenv**: Variables de entorno
- **logrus** o **zap**: Logging estructurado
- **viper**: Configuración

## 🔄 Plan de Migración Paso a Paso

### Semana 1: Setup y Fundación
1. **Día 1-2**: Setup inicial del proyecto Go
   - Inicializar módulo Go
   - Configurar estructura de directorios
   - Setup Docker y docker-compose

2. **Día 3-4**: Implementar capa de dominio
   - Entidades básicas (User, CryptoAsset)
   - Value objects
   - Interfaces de repositorio

3. **Día 5**: Setup de base de datos
   - Configuración MongoDB
   - Implementación de repositorios básicos

### Semana 2: Autenticación y Core Features
1. **Día 1-2**: Sistema de autenticación
   - JWT service
   - Middleware de autenticación
   - Endpoints de registro/login

2. **Día 3-4**: CRUD básico
   - Gestión de usuarios
   - Gestión de crypto assets
   - Testing básico

3. **Día 5**: Validación y error handling
   - Middleware de validación
   - Manejo centralizado de errores

### Semana 3: Portfolio y Transacciones
1. **Día 1-2**: Entidades complejas
   - Portfolio entity
   - Transaction entity
   - Relaciones entre entidades

2. **Día 3-4**: Use cases avanzados
   - Gestión de portfolios
   - Sistema de transacciones
   - Agregaciones y cálculos

3. **Día 5**: Testing de integración
   - Tests end-to-end
   - Performance testing

### Semana 4: Integración Bitso y Finalización
1. **Día 1-2**: Cliente Bitso
   - HTTP client con rate limiting
   - Autenticación HMAC
   - Modelos de respuesta

2. **Día 3-4**: Trading service
   - Integración con Bitso API
   - Endpoints de trading
   - Manejo de errores de API externa

3. **Día 5**: Documentación y deployment
   - Swagger/OpenAPI docs
   - CI/CD pipeline
   - Optimización de performance

## 📊 Comparativa de Performance Esperada

| Métrica | Python/FastAPI | Go | Mejora Esperada |
|---------|----------------|----|-----------------| 
| Throughput (req/s) | ~1,000 | ~10,000 | 10x |
| Latencia (ms) | 50-100 | 5-10 | 5-10x |
| Memoria (MB) | 100-200 | 20-50 | 2-4x |
| Tiempo de startup | 2-3s | 0.1-0.5s | 4-6x |
| Tamaño binario | N/A | 15-30MB | Deployable |

## 🎯 Beneficios de la Migración

### Performance
- **Concurrencia nativa**: Goroutines vs threads/async
- **Compilación**: Binario optimizado vs interpretado
- **Garbage Collector**: Más eficiente para alta carga

### Operacional
- **Single binary**: Deployment simplificado
- **Cross-compilation**: Build para múltiples plataformas
- **Menor footprint**: Menos recursos de servidor

### Desarrollo
- **Type safety**: Compilación estática vs runtime errors
- **Tooling**: Excelente ecosistema de herramientas
- **Concurrencia**: Primitivas nativas para programación concurrente

## 📝 Notas de Implementación

### Diferencias Clave Python → Go

1. **Error Handling**
```python
# Python
try:
    result = risky_operation()
except Exception as e:
    handle_error(e)
```

```go
// Go
result, err := riskyOperation()
if err != nil {
    return handleError(err)
}
```

2. **Dependency Injection**
```python
# Python (FastAPI)
@app.get("/users")
def get_users(user_service: UserService = Depends(get_user_service)):
    return user_service.get_all()
```

```go
// Go (Manual DI)
type Handler struct {
    userService *UserService
}

func (h *Handler) GetUsers(c *gin.Context) {
    users := h.userService.GetAll()
    c.JSON(200, users)
}
```

3. **Async/Await → Goroutines**
```python
# Python
async def fetch_data():
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()
```

```go
// Go
func fetchData(ctx context.Context) (Data, error) {
    resp, err := http.Get(url)
    if err != nil {
        return Data{}, err
    }
    defer resp.Body.Close()
    
    var data Data
    err = json.NewDecoder(resp.Body).Decode(&data)
    return data, err
}
```

## 🚀 Comandos de Desarrollo

### Setup inicial
```bash
# Crear proyecto
mkdir go-mycrypto && cd go-mycrypto
go mod init github.com/username/go-mycrypto

# Instalar dependencias
go get github.com/gin-gonic/gin
go get go.mongodb.org/mongo-driver/mongo
go get github.com/golang-jwt/jwt/v5
go get golang.org/x/crypto/bcrypt

# Desarrollo
go run cmd/server/main.go

# Testing
go test ./...

# Build
go build -o bin/server cmd/server/main.go

# Docker
docker build -t go-mycrypto .
docker run -p 8080:8080 go-mycrypto
```

Esta bitácora proporciona una guía completa para recrear la funcionalidad de MyCrypto API en Go, manteniendo la arquitectura limpia y mejorando significativamente el performance y la eficiencia operacional.
