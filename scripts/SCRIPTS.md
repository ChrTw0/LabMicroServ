# 🛠️ Scripts de Docker - Guía Rápida

Scripts para manejar fácilmente el sistema de microservicios con Docker.

## 📋 Scripts Disponibles

| Script | Descripción | Uso |
|--------|-------------|-----|
| `start.sh` | Inicia todos los servicios | `./start.sh` |
| `stop.sh` | Detiene todos los servicios | `./stop.sh` |
| `restart.sh` | Reinicia servicios | `./restart.sh [servicio]` |
| `status.sh` | Muestra el estado | `./status.sh` |
| `logs.sh` | Muestra logs en tiempo real | `./logs.sh [servicio]` |
| `build.sh` | Construye las imágenes | `./build.sh [servicio]` |
| `db-only.sh` | Solo inicia las bases de datos | `./db-only.sh` |
| `shell.sh` | Abre shell en un contenedor | `./shell.sh <servicio>` |
| `clean.sh` | Limpia todo (⚠️ BORRA DATOS) | `./clean.sh` |

---

## 🚀 Flujo de Trabajo Típico

### **Primera vez (Setup inicial):**

```bash
# 1. Construir las imágenes
./build.sh

# 2. Iniciar todo
./start.sh

# 3. Ver estado
./status.sh
```

### **Desarrollo diario:**

```bash
# Iniciar servicios
./start.sh

# Ver logs de un servicio específico
./logs.sh user-service

# Reiniciar después de cambios
./restart.sh user-service

# Al terminar
./stop.sh
```

### **Solo desarrollo local (sin Docker en servicios):**

```bash
# Solo bases de datos en Docker
./db-only.sh

# Luego ejecuta cada servicio manualmente:
cd user-service
uvicorn src.main:app --reload --port 8001
```

---

## 📖 Ejemplos de Uso

### **Iniciar todo el sistema:**
```bash
./start.sh
```

### **Ver logs de un servicio específico:**
```bash
./logs.sh user-service
./logs.sh patient-service
```

### **Ver logs de TODOS los servicios:**
```bash
./logs.sh
```

### **Reiniciar un servicio después de cambios:**
```bash
./restart.sh user-service
```

### **Entrar al shell de un servicio:**
```bash
# Shell del contenedor
./shell.sh user-service

# Conectar a PostgreSQL
./shell.sh user-db
```

### **Ver estado de todo:**
```bash
./status.sh
```

### **Reconstruir un servicio:**
```bash
./build.sh user-service
./restart.sh user-service
```

### **Limpiar todo y empezar de cero:**
```bash
./clean.sh     # ⚠️ ELIMINA DATOS
./build.sh
./start.sh
```

---

## 🔧 Comandos Docker Directos (Alternativa)

Si prefieres usar Docker Compose directamente:

```bash
# Iniciar
docker-compose up -d

# Detener
docker-compose down

# Ver logs
docker-compose logs -f user-service

# Reconstruir
docker-compose build user-service

# Reiniciar
docker-compose restart user-service

# Estado
docker-compose ps

# Shell
docker-compose exec user-service bash
```

---

## 💡 Tips

1. **Logs en tiempo real:** Los scripts de logs se mantienen abiertos mostrando logs en vivo. Presiona `Ctrl+C` para salir.

2. **Reinicio rápido:** Después de cambiar código, usa `./restart.sh <servicio>` en lugar de detener todo.

3. **Solo DBs:** Para desarrollo local sin Docker en los servicios, usa `./db-only.sh`.

4. **Limpieza:** `./clean.sh` elimina TODO (contenedores, volúmenes, datos). Úsalo solo si quieres empezar de cero.

5. **Shell interactivo:**
   - `./shell.sh user-service` → Bash en el contenedor
   - `./shell.sh user-db` → PostgreSQL CLI

---

## 🐛 Troubleshooting

### **Error: "Cannot start service..."**
```bash
# Detener todo y limpiar
./stop.sh
./clean.sh

# Reconstruir y reiniciar
./build.sh
./start.sh
```

### **Base de datos no responde**
```bash
# Ver logs de la BD
./logs.sh user-db

# Reiniciar la BD
./restart.sh user-db
```

### **Puerto ya en uso**
```bash
# Ver qué servicios están corriendo
./status.sh

# O ver puertos ocupados
netstat -ano | findstr :8001
```

### **Cambios no se reflejan**
```bash
# Reconstruir la imagen
./build.sh user-service

# Reiniciar el servicio
./restart.sh user-service
```

---

## 📌 Notas Importantes

- ⚠️ `./clean.sh` **ELIMINA TODOS LOS DATOS** de la base de datos
- Los scripts usan Git Bash en Windows (viene con Git)
- Si no tienes Git Bash, usa los comandos Docker Compose directos
- Los logs se guardan también en `<servicio>/logs/`

---

**Última actualización:** 19 de noviembre de 2025
