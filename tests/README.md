# MyCrypto API Automated Testing

Sistema de pruebas automatizadas para todos los endpoints de la API MyCrypto con gestión completa del ciclo de vida de Docker.

## 🚀 Características

- **Aislamiento completo**: Cada prueba ejecuta su propio ciclo Docker (levantar → probar → limpiar → bajar)
- **Gestión automática de datos**: Limpieza automática de datos de prueba después de cada test
- **Autenticación automática**: Registro y login automático para pruebas que requieren auth
- **Reportes detallados**: Estadísticas completas de ejecución y resultados

## 📁 Estructura

```
tests/
├── README.md                    # Este archivo
├── requirements.txt             # Dependencias de testing
├── run_endpoint_tests.py        # Script principal de testing
├── unit/
│   └── test_endpoints.py        # Clases de pruebas por endpoint
└── postman/                     # Colecciones Postman (legacy)
```

## 🛠 Instalación

```bash
# Instalar dependencias de testing
pip install -r tests/requirements.txt
```

## 🧪 Ejecución de Pruebas

### Ejecutar todas las pruebas
```bash
# Usando Makefile (recomendado)
make test-endpoints

# Directamente
./run_tests.sh
```

### Ejecutar pruebas por categoría
```bash
# Pruebas de autenticación
make test-auth

# Pruebas de crypto assets
make test-crypto

# Pruebas de portfolios
make test-portfolio

# Pruebas de transacciones
make test-transaction
```

### Ejecutar prueba específica
```bash
# Usando Makefile
make test-endpoint TEST=auth_register

# Directamente
./run_tests.sh auth_register
```

## 📋 Pruebas Disponibles

### Autenticación
- `auth_register` - Registro de usuario
- `auth_login` - Login de usuario

### Crypto Assets
- `crypto_list` - Listar crypto assets
- `crypto_create` - Crear crypto asset

### Portfolios
- `portfolio_list` - Listar portfolios
- `portfolio_create` - Crear portfolio

### Transacciones
- `transaction_list` - Listar transacciones
- `transaction_buy` - Flujo completo de compra
- `transaction_stats` - Estadísticas de transacciones

## 🔄 Ciclo de Vida de Cada Prueba

1. **Inicio**: Levantar ambiente Docker (`make dev`)
2. **Preparación**: Esperar que la API esté lista (health check)
3. **Autenticación**: Registrar usuario de prueba si es necesario
4. **Ejecución**: Ejecutar la prueba específica
5. **Limpieza**: Bajar ambiente Docker (`make dev-down`)
6. **Purga**: Limpiar volúmenes y contenedores (`docker system prune`)

## 📊 Ejemplo de Salida

```
🧪 Running: TestAuthEndpoints.test_auth_register
============================================================
🚀 Starting Docker environment...
✅ API is ready
📝 Register Test Result: {'success': True, 'status_code': 200, ...}
✅ PASSED in 15.23s
🛑 Stopping Docker environment...
🧹 Cleaning Docker environment...
```

## 🎯 Ventajas del Sistema

- **Aislamiento**: Cada prueba es independiente
- **Limpieza**: No hay contaminación entre pruebas
- **Realismo**: Pruebas en ambiente real con Docker
- **Automatización**: Sin intervención manual
- **Reportes**: Estadísticas detalladas de ejecución

## 🔧 Configuración

Las pruebas están configuradas para:
- **URL Base**: `http://localhost:8000`
- **Timeout**: 30 segundos para health check
- **Usuario de prueba**: `test@example.com` / `TestPassword123!`

---

# API Testing Files (Legacy)

Esta sección contiene archivos `.http` para probar la API manualmente.

## Archivos de Testing

### `quick-test.http`
**Uso**: Prueba rápida de funcionalidad básica
- Health check
- Crear usuario y asset
- Crear entrada de portfolio
- Verificar endpoints básicos

### `api.http`
**Uso**: Testing completo de todos los endpoints
- Todos los endpoints de usuarios
- Todos los endpoints de crypto assets
- Todos los endpoints de portfolio
- Incluye operaciones CRUD completas

### `test-scenarios.http`
**Uso**: Escenarios de testing complejos
- Flujo completo usuario → portfolio
- Testing de actualizaciones de precios
- Gestión avanzada de portfolio
- Testing de manejo de errores
- Testing de paginación
- Testing de conexión a base de datos

### `environment.http`
**Uso**: Variables de entorno para los tests
- URLs base y configuración
- IDs de ejemplo para reemplazar
- Datos de prueba predefinidos

## Cómo usar

### 1. Instalar extensión HTTP Client
- **VS Code**: REST Client extension
- **IntelliJ/WebStorm**: HTTP Client (built-in)
- **Postman**: Importar como colección

### 2. Iniciar el servidor
```bash
# Instalar dependencias
pip install -r requirements.txt

# Iniciar MongoDB (si usas local)
brew services start mongodb-community

# Ejecutar servidor
python main.py
```

### 3. Ejecutar tests

#### Opción A: VS Code con REST Client
1. Abrir archivo `.http`
2. Hacer clic en "Send Request" sobre cada endpoint
3. Ver respuestas en panel lateral

#### Opción B: Línea de comandos con curl
```bash
# Health check
curl http://localhost:8000/health

# Crear usuario
curl -X POST http://localhost:8000/users/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","name":"Test User","password":"test123"}'
```

### 4. Flujo de testing recomendado

1. **Empezar con `quick-test.http`**
   - Verificar que todo funciona básicamente
   - Obtener IDs reales para usar en otros tests

2. **Usar `test-scenarios.http`**
   - Reemplazar placeholders con IDs reales
   - Ejecutar escenarios completos

3. **Usar `api.http`** para testing detallado
   - Probar todos los endpoints individualmente
   - Verificar edge cases

## Variables a reemplazar

En los archivos encontrarás placeholders como:
- `{{user_id}}` → ID real del usuario creado
- `{{asset_id}}` → ID real del asset creado
- `{{portfolio_id}}` → ID real de la entrada de portfolio

**Importante**: Reemplaza estos valores con IDs reales obtenidos de las respuestas de la API.

## Endpoints disponibles

### Health & Info
- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /docs` - API documentation (Swagger)

### Users
- `POST /users/` - Crear usuario
- `GET /users/` - Listar usuarios
- `GET /users/{id}` - Obtener usuario
- `PUT /users/{id}` - Actualizar usuario
- `DELETE /users/{id}` - Eliminar usuario
- `GET /users/email/{email}` - Buscar por email

### Crypto Assets
- `POST /crypto-assets/` - Crear asset
- `GET /crypto-assets/` - Listar assets
- `GET /crypto-assets/{id}` - Obtener asset
- `PUT /crypto-assets/{id}` - Actualizar asset
- `DELETE /crypto-assets/{id}` - Eliminar asset
- `GET /crypto-assets/symbol/{symbol}` - Buscar por símbolo

### Portfolio
- `POST /portfolio/` - Crear entrada
- `GET /portfolio/` - Listar entradas
- `GET /portfolio/{id}` - Obtener entrada
- `PUT /portfolio/{id}` - Actualizar entrada
- `DELETE /portfolio/{id}` - Eliminar entrada
- `GET /portfolio/user/{user_id}` - Portfolio de usuario

## Troubleshooting

### Error: Connection refused
- Verificar que el servidor esté ejecutándose en puerto 8000
- Verificar que MongoDB esté ejecutándose

### Error: Database connection
- Verificar configuración en `.env`
- Verificar que MongoDB esté accesible

### Error: Validation error
- Verificar formato JSON en requests
- Verificar que todos los campos requeridos estén presentes

### Error: 404 Not Found
- Verificar que los IDs existan en la base de datos
- Usar IDs reales obtenidos de respuestas previas
