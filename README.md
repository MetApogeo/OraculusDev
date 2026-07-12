<p align="center">
  <img src="docs/src/oraculus%20svg.svg" width="180" alt="Oraculus Logo" />
</p>

# Oraculus: Telemetría Financiera y Auditoría de Deuda Técnica

**Oraculus** es un motor analítico avanzado y una herramienta de interfaz de línea de comandos (CLI) diseñada para cerrar la brecha de comunicación entre el desarrollo técnico y los tomadores de decisiones empresariales. Traduce las métricas complejas de repositorios de software (commits, complejidad ciclomática y volumen de cambios) en **indicadores financieros claros, tangibles e interactivos**.

---

### ¿Por qué Oraculus?

En la gestión de proyectos de software, la velocidad de desarrollo suele desconectarse de la realidad financiera. **Oraculus** soluciona esto a través de tres pilares operativos:
1. **Auditoría Financiera Real ($C_{real}$):** Calcula el valor real del esfuerzo invertido de desarrollo cruzando los commits del equipo con el salario estimado y el tiempo de implementación.
2. **Semáforo de Eficiencia ($IEF$):** Determina el Índice de Eficiencia Financiera comparando el costo consumido contra el presupuesto asignado, alertando inmediatamente ante desvíos presupuestarios.
3. **Análisis de Riesgo y Deuda Técnica:** Identifica commits que degradan la calidad del código, estimando el costo de la Deuda Técnica acumulada y evaluando el Riesgo de Negocio (probabilidad de retrasos) para decisiones de PM proactivas.

---

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
- `--python`: Flag para forzar de forma inmediata el análisis de calidad con Radon para Python.
- `--php`: Flag para forzar de forma inmediata el análisis para PHP (Próximamente).
- `--js`: Flag para forzar de forma inmediata el análisis para JavaScript (Próximamente).
*(Nota: Si no se ingresa ningún flag de lenguaje por CLI, la aplicación te preguntará si deseas hacer el análisis de calidad o prefieres omitirlo para mayor velocidad).*

### Ejemplo de Ejecución

```bash
oraculus analyze --repo . --salario 3000 --limite 12
```

### Flujo de Análisis y Semáforo de Eficiencia

Al finalizar las tablas detalladas de commits normales e independientes (outliers), la CLI te solicitará el **Presupuesto Estimado ($C_{esp}$)**. Al ingresarlo, calculará el **Índice de Eficiencia Financiera ($IEF$)** mostrando el estado con colores Cyberpunk en base a la tolerancia estándar del 20%:

- **$IEF < 0.8$:** `[OK] Termino mas rapido de lo esperado` (Verde Neón)
- **$0.8 \le IEF \le 1.2$:** `[OK] Rango aceptable (Dentro de lo esperado)` (Lavanda/Amarillo)
- **$IEF > 1.2$:** `[ALERTA] Presupuesto excedido` (Rojo Neón)

### 📊 Reportes HTML Interactivos

Al finalizar el análisis desde la terminal, la CLI te preguntará si deseas generar un reporte interactivo en formato HTML:
```text
¿Desea generar un reporte HTML? [Y/n]: Y
```
Esto guardará el archivo en la carpeta local `oraculus_reports/` y lo abrirá automáticamente en tu navegador predeterminado. El reporte contiene:
- **Gráficas Plotly Cyberpunk:** Un gráfico de barras horizontales interactivo con el costo por commit (coloreado según la calidad del código) y un gráfico de pastel con la distribución porcentual de calidad.
- **Isotipo e Identidad Visual:** Integra el isotipo vectorial original renderizado directamente en SVG con degradados neón.
- **Riesgo de Negocio & Deuda Técnica:** Muestra de forma destacada la tarjeta de riesgo y recomendaciones clave para Project Managers.
- **Exportación nativa a PDF:** Incluye un botón interactivo `⬇ Exportar como PDF` optimizado mediante reglas CSS `@media print` para ocultar botones, apilar gráficos y mantener los degradados y colores oscuros en la impresión en Chrome, Firefox y Edge.

### 📜 Historial de Análisis (`oraculus history`)

Oraculus registra automáticamente el historial de todos tus reportes generados en `oraculus_reports/index.json` (el cual queda ignorado en Git de forma segura). El comando `history` proporciona herramientas avanzadas para dar seguimiento al repositorio:

```bash
oraculus history [OPCIONES]
```

#### Opciones de Historial

* **Listar Historial:** Muestra la lista de todos los análisis generados en formato de tabla cyberpunk, con colores dinámicos basados en el riesgo de negocio del proyecto:
  ```bash
  oraculus history
  ```
  Al final de la tabla, si cuentas con más de un análisis para el último repositorio analizado, se mostrará el panel de **Tendencia** detallando la evolución de tu IEF y Deuda Técnica acumulada:
  ```text
  +-------- === TENDENCIA: MetApogeo/OraculusDev === --------+
  |   IEF:   0.14 -> 2.07 -> 0.90 [^ Deteriorando]           |
  |   Deuda: $0 -> $0 -> $0 [= Estable]                      |
  +----------------------------------------------------------+
  ```
* **Abrir Reportes (`--open`):** Abre directamente en tu navegador predeterminado el reporte HTML guardado bajo el ID seleccionado:
  ```bash
  oraculus history --open 3
  ```
* **Estadísticas Consolidadas (`--stats`):** Muestra el promedio general de IEF, peor análisis (mayor desvío), mejor análisis y costo acumulado de deuda técnica:
  ```bash
  oraculus history --stats
  ```
* **Comparación Lado a Lado (`--compare`):** Contrasta de forma estructurada dos análisis específicos en columnas lado a lado:
  ```bash
  oraculus history --compare 1 3
  ```
* **Limpieza Interactiva (`--clean`):** Despliega un menú en terminal para eliminar reportes antiguos (pudiendo vaciar todo el historial o conservar únicamente los últimos 3 análisis):
  ```bash
  oraculus history --clean
  ```

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
