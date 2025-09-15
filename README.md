# MyCrypto FastAPI Backend v2.0

Una aplicación FastAPI para gestión de portafolios de criptomonedas con **arquitectura desacoplada** que soporta múltiples bases de datos (MongoDB, Firebase/Firestore).

## 🚀 Características

- **FastAPI**: Framework web moderno y rápido para construir APIs
- **Arquitectura Desacoplada**: Patrón Repository para intercambiar bases de datos
- **MongoDB**: Soporte nativo con Motor (async)
- **Firebase/Firestore**: Soporte opcional
- **Pydantic**: Validación de datos y serialización
- **CORS**: Configurado para desarrollo frontend
- **Database Agnostic**: Cambia de base de datos sin modificar código

## 📁 Estructura del Proyecto

```
pyBackend/
├── main.py                    # Aplicación principal FastAPI
├── config.py                  # Configuración y variables de entorno
├── database.py                # Factory de conexiones de base de datos
├── models.py                  # Modelos Pydantic (DTOs y entidades)
├── repositories/              # Patrón Repository
│   ├── __init__.py
│   ├── base.py               # Interfaces abstractas
│   └── mongodb.py            # Implementación MongoDB
├── docker/                   # Configuración Docker
│   └── mongo-init.js         # Script inicialización MongoDB
├── requirements.txt           # Dependencias Python
├── .env.example              # Ejemplo de variables de entorno
└── README.md                 # Este archivo
```

## 🐳 Docker Setup (Recomendado)

### Opción 1: Desarrollo con Docker Compose

```bash
# Construir y ejecutar todos los servicios
docker-compose -f docker-compose.dev.yml up --build

# Ejecutar en background
docker-compose -f docker-compose.dev.yml up -d --build

# Ver logs
docker-compose -f docker-compose.dev.yml logs -f api

# Parar servicios
docker-compose -f docker-compose.dev.yml down
```

### Opción 2: Producción con Docker Compose

```bash
# Ejecutar en modo producción
docker-compose up --build -d

# Ver logs
docker-compose logs -f api

# Parar servicios
docker-compose down
```

### Servicios incluidos:
- **API FastAPI**: `http://localhost:8000`
- **MongoDB**: `localhost:27017`
- **Mongo Express**: `http://localhost:8081` (admin/admin123)

## ⚙️ Configuración Manual

### 1. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 2. Configurar Variables de Entorno

Copia `.env.example` a `.env`:

```bash
cp .env.example .env
```

### 3. Configurar Base de Datos

#### Para MongoDB (por defecto):
```env
DATABASE_TYPE=mongodb
DATABASE_NAME=mycrypto
MONGODB_URL=mongodb://localhost:27017/mycrypto
```

#### Para MongoDB Atlas:
```env
DATABASE_TYPE=mongodb
DATABASE_NAME=mycrypto
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/mycrypto
```

#### Para Firebase/Firestore (opcional):
```env
DATABASE_TYPE=firestore
FIREBASE_CREDENTIALS_PATH=/path/to/firebase-credentials.json
FIREBASE_PROJECT_ID=your-firebase-project-id
```

### 4. Instalar MongoDB (si usas local)

```bash
# macOS
brew install mongodb-community

# Iniciar MongoDB
brew services start mongodb-community
```

### 5. Ejecutar la Aplicación

```bash
python main.py
```

O usando uvicorn:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

La API estará disponible en: http://localhost:8000

## 📚 Documentación de la API

- **Documentación interactiva (Swagger)**: http://localhost:8000/docs
- **Documentación alternativa (ReDoc)**: http://localhost:8000/redoc

## 🔗 Endpoints Principales

### Usuarios
- `POST /users/` - Crear usuario
- `GET /users/` - Obtener usuarios (con paginación)
- `GET /users/{user_id}` - Obtener usuario específico
- `PUT /users/{user_id}` - Actualizar usuario
- `DELETE /users/{user_id}` - Eliminar usuario
- `GET /users/email/{email}` - Buscar usuario por email

### Criptomonedas
- `POST /crypto-assets/` - Crear activo cripto
- `GET /crypto-assets/` - Obtener activos (con paginación)
- `GET /crypto-assets/{asset_id}` - Obtener activo específico
- `PUT /crypto-assets/{asset_id}` - Actualizar activo
- `DELETE /crypto-assets/{asset_id}` - Eliminar activo
- `GET /crypto-assets/symbol/{symbol}` - Buscar por símbolo

### Portafolio
- `POST /portfolio/` - Crear entrada de portafolio
- `GET /portfolio/` - Obtener todas las entradas (con paginación)
- `GET /portfolio/{portfolio_id}` - Obtener entrada específica
- `PUT /portfolio/{portfolio_id}` - Actualizar entrada
- `DELETE /portfolio/{portfolio_id}` - Eliminar entrada
- `GET /portfolio/user/{user_id}` - Obtener portafolio de usuario

## 📊 Modelos de Datos

### Usuario
```json
{
  "email": "usuario@ejemplo.com",
  "name": "Nombre Usuario",
  "password": "contraseña_segura"
}
```

### Activo Cripto
```json
{
  "symbol": "BTC",
  "name": "Bitcoin",
  "current_price": 45000.00
}
```

### Entrada de Portafolio
```json
{
  "user_id": "user_id_string",
  "asset_id": "asset_id_string",
  "quantity": 0.5,
  "purchase_price": 44000.00
}
```

## 🏗️ Arquitectura

### Patrón Repository
La aplicación usa el patrón Repository para desacoplar la lógica de negocio de la persistencia:

```python
# Cambiar de base de datos es tan simple como:
DATABASE_TYPE=firestore  # en lugar de mongodb
```

### Interfaces Abstractas
- `BaseRepository`: Operaciones CRUD básicas
- `UserRepository`: Operaciones específicas de usuarios
- `CryptoAssetRepository`: Operaciones específicas de criptomonedas
- `PortfolioRepository`: Operaciones específicas de portafolio

### Factory Pattern
`DatabaseFactory` maneja la creación de conexiones y repositorios según la configuración.

## 🔄 Cambiar de Base de Datos

### De MongoDB a Firestore:

1. Instala dependencias de Firebase:
```bash
pip install firebase-admin google-cloud-firestore
```

2. Configura variables de entorno:
```env
DATABASE_TYPE=firestore
FIREBASE_CREDENTIALS_PATH=/path/to/credentials.json
FIREBASE_PROJECT_ID=your-project-id
```

3. Reinicia la aplicación - ¡No se requieren cambios de código!

## 🧪 Desarrollo

### Agregar Nueva Base de Datos

1. Crea implementación en `repositories/nueva_db.py`
2. Implementa las interfaces abstractas de `repositories/base.py`
3. Agrega soporte en `database.py` factory
4. Actualiza `config.py` con nuevas variables

### Estructura de Repositorios

```python
class NuevaDBUserRepository(UserRepository[UserResponse]):
    async def create(self, data: Dict[str, Any]) -> UserResponse:
        # Implementación específica
        pass
    
    async def get_by_email(self, email: str) -> Optional[UserResponse]:
        # Implementación específica
        pass
```

## 🔒 Seguridad

⚠️ **Notas de Seguridad para Producción**:
- Hashear contraseñas (bcrypt, argon2)
- Configurar CORS apropiadamente
- Usar HTTPS
- Implementar autenticación JWT
- Validar y sanitizar entradas
- Rate limiting
- Logging de seguridad

## 🚀 Próximos Pasos

- [ ] Implementar autenticación JWT
- [ ] Agregar hash de contraseñas (bcrypt)
- [ ] Integrar API de precios en tiempo real
- [ ] Agregar tests unitarios y de integración
- [ ] Implementar logging estructurado
- [ ] Agregar cache (Redis)
- [ ] Implementar WebSockets para precios en tiempo real
- [ ] Agregar más validaciones de negocio
- [ ] Documentación de arquitectura
- [ ] CI/CD pipeline

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request
