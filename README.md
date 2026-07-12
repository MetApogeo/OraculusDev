# 👁️ Oraculus: Financial Repo Analytics

**Oraculus** es una herramienta de interfaz de línea de comandos (CLI) diseñada para transformar métricas técnicas de repositorios (GitHub/Jira) en indicadores financieros claros para stakeholders. Permite calcular el costo real de desarrollo basado en el esfuerzo técnico y la eficiencia operativa.

## 📜 La Historia Detrás del Código

El desarrollo de Oraculus no empezó frente a un monitor, sino en los espacios entre clases y horas libres durante mi labor como profesor.

### 1. Las Primeras Semillas (Bocetos en Papel)

Todo comenzó con la necesidad de centralizar la comunicación entre ramas de GitHub y tareas de Jira. Estos esquemas iniciales fueron trazados "entre clases", capturando la esencia de lo que hoy es el ecosistema de análisis.

![image alt](https://github.com/MetApogeo/OraculusDev/blob/f732e9130c537b9e068e3f364435c52b7e059ef1/docs/img/hoja_ruta_boceto1.jpg)
_Figura 1: Arquitectura inicial de flujo entre Jira, GitHub y el cálculo de Story Points._

![image alt](https://github.com/MetApogeo/OraculusDev/blob/f732e9130c537b9e068e3f364435c52b7e059ef1/docs/img/hoja_ruta_boceto2.jpg)
_Figura 2: Definición de esquemas estrictos con Pydantic y la lógica de mappers entre PHP y Python._

### 2. La Formalización Matemática (La Pizarra)

Durante una hora libre, las ideas se convirtieron en fórmulas. El **7 de mayo de 2026**, definí la lógica financiera que rige el sistema actual, incluyendo el filtro de **Rango Intercuartílico (IQR)** para detectar anomalías en los commits.

![image alt](https://github.com/MetApogeo/OraculusDev/blob/f732e9130c537b9e068e3f364435c52b7e059ef1/docs/img/pizarra_calculo1.jpg)
_Figura 3: Definición del Índice de Eficiencia Financiera ($IEF$) y fórmulas de costo por commit._

---

## 🛠️ Estado Actual del Desarrollo

Hoy, Oraculus ha evolucionado de garabatos en papel a una herramienta CLI funcional que aplica principios sólidos de ingeniería de software:

- **Arquitectura DTO:** Uso de `dataclasses` para el transporte de datos limpio y tipado.
- **Responsabilidad Única (SRP):** El sistema está dividido en estaciones: conectores de datos, lógica de métricas (Calculadora) y presentación (CLI).
- **Análisis Git Local Seguro:** Copia automática de repositorios locales a caché para comparaciones seguras sin interferir en el workspace activo del desarrollador.

### Lógica Financiera Implementada

El sistema calcula actualmente el costo de la siguiente manera:

1. **Costo por Hora ($C_h$):**
   $$C_h = \frac{\text{Salario Mensual}}{\text{Horas Efectivas}}$$

2. **Tiempo por Commit ($T_{horas}$):**
   $$T_{horas} = \frac{LOC_{commit}}{60}$$

3. **Costo del Commit ($C_{commit}$):**
   $$C_{commit} = C_h \cdot T_{horas}$$

4. **Estimación de Deuda Técnica ($C_{deuda}$):**
   $$C_{deuda} = 3 \cdot \sum C_{commit\_deuda}$$
   (Estimación a futuro con un factor multiplicador de 3x).

---

## 📦 Instalacion

1. **Clonar el repositorio:**

   ```bash
   git clone https://github.com/MetApogeo/OraculusDev.git
   cd OraculusDev
   ```

2. **Instalar el proyecto de forma global en modo editable:**

   ```bash
   pip install -e .
   ```

   Esto instalará todas las dependencias requeridas (`requests`, `python-dotenv`, `click`, `rich`) y registrará el comando `oraculus` en tu terminal de forma global.

3. **(Opcional) Configurar GITHUB_TOKEN:**
   Crea un archivo `.env` en la raíz del proyecto para evitar límites de tasa al analizar repositorios remotos vía API de GitHub:
   ```env
   GITHUB_TOKEN=tu_token_aqui
   ```

---

## 🚀 Uso

El comando principal de la aplicación es `oraculus analyze`:

```bash
oraculus analyze [OPCIONES]
```

### Opciones Disponibles

- `--repo TEXT`: Ruta local del repositorio (por ejemplo, `.`) o repositorio remoto en formato `usuario/repo` (por ejemplo, `MetApogeo/OraculusDev`). [Por defecto: `.`].
- `--limite INTEGER`: Número de commits a analizar en el historial. [Por defecto: `10`].
- `--salario FLOAT`: Salario mensual promedio en USD. Si se omite, la CLI te lo solicitará de forma interactiva.
- `--horas INTEGER`: Horas efectivas trabajadas al mes. [Por defecto: `160`].
- `--loc-por-hora FLOAT`: Promedio de Líneas de Código (LOC) escritas por hora. [Por defecto: `60.0`].

### Ejemplo de Ejecución

```bash
oraculus analyze --repo . --salario 3000 --limite 12
```

### Flujo de Análisis y Semáforo de Eficiencia

Al finalizar las tablas detalladas de commits normales e independientes (outliers), la CLI te solicitará el **Presupuesto Estimado ($C_{esp}$)**. Al ingresarlo, calculará el **Índice de Eficiencia Financiera ($IEF$)** mostrando el estado con colores Cyberpunk en base a la tolerancia estándar del 20%:

- **$IEF < 0.8$:** `[OK] Termino mas rapido de lo esperado` (Verde Neón)
- **$0.8 \le IEF \le 1.2$:** `[OK] Rango aceptable (Dentro de lo esperado)` (Lavanda/Amarillo)
- **$IEF > 1.2$:** `[ALERTA] Presupuesto excedido` (Rojo Neón)

---

## 🚀 Hoja de Ruta (Roadmap)

Aunque el núcleo es funcional, el proyecto se encuentra en una fase de optimización continua:

- [ ] **Migración a GraphQL:** Para resolver el problema de $N+1$ llamadas y obtener todos los datos en una sola petición.
- [x] **Análisis Git Local:** Implementación de lectura directa de la carpeta `.git` para máxima velocidad sin dependencia de API.
- [ ] **Integración con Jira:** Siguiendo los bocetos originales para cruzar costos con Story Points.

---

## 📄 Licencia

Este proyecto es de código abierto (Open Source).

> _"De la pizarra al despliegue: Arquitectura sistémica para decisiones lógicas."_

---
