# 🔬 INVESTIGACIÓN: NOVANET

**Fecha:** 20 Noviembre 2025
**Estado:** Investigación completada - NO VIABLE PARA SCRAPING PÚBLICO
**Conclusión:** ⚠️ Sistema interno de gestión federativa con acceso restringido

---

## 📋 ¿QUÉ ES NOVANET?

**Novanet** es una **plataforma de gestión deportiva** para federaciones de fútbol en España.

### Historia:
- **2005**: Creado inicialmente para la Federación de Madrid
- **2017**: Expandido a 12 federaciones territoriales
- **2021**: **Comprado por la RFEF** por 1,25 millones€ (financiado con fondos UEFA)
- **2022-2024**: Migración de TODAS las federaciones territoriales a Novanet (unificación tecnológica)

### Cobertura actual:
- **18 federaciones territoriales** españolas (prácticamente todas)
- **1 federación nacional** (Andorra)
- **750,000+ licencias** gestionadas
- **650,000+ partidos** por temporada

---

## 🏆 FEDERACIONES QUE USAN NOVANET (2024)

### ✅ Federaciones confirmadas (18):

| Federación | Subdominio/URL | Estado |
|------------|----------------|--------|
| Madrid | rffm.es | ✅ Activo |
| Castilla-La Mancha | - | ✅ Activo |
| Baleares | - | ✅ Activo |
| La Rioja | - | ✅ Activo |
| Aragón | - | ✅ Activo |
| Cataluña | - | ✅ Activo |
| Extremadura | - | ✅ Activo |
| Andalucía | - | ✅ Activo |
| Galicia | - | ✅ Activo |
| Murcia | webffrm.novanet.es | ✅ Activo |
| Cantabria | - | ✅ Activo |
| Ceuta | - | ✅ Activo |
| **Comunidad Valenciana** | ffcv.es + Novanet | ✅ Migrado 12/2022 |
| **Asturias** | asturfutbol.es/pnfg | ✅ Migrado 2023 |
| **Castilla y León** | fcylf.novanet.es / intranet.rfcylf.es | ✅ Migrado 2023 |
| **Navarra** | fnf.novanet.es | ✅ Migrado 2023 |
| **Melilla** | - | ✅ Migrado 2023 |
| **Canarias** | - | ✅ Migrado 2024 |

### Patrón de URLs:
```
https://[codigo].novanet.es/pnfg/NPcd/[Modulo]?parametros
https://[federacion].es/pnfg/NPcd/[Modulo]?parametros
```

**Ejemplos:**
- `webffrm.novanet.es` (Murcia)
- `fcylf.novanet.es` (Castilla y León)
- `fnf.novanet.es` (Navarra)
- `asturfutbol.es/pnfg` (Asturias)
- `rffm.es` (Madrid)

---

## 🔧 FUNCIONALIDADES DE NOVANET

### Para Federaciones:
- ✅ Gestión de competiciones (ligas, copas, play-offs)
- ✅ Clasificaciones y resultados
- ✅ Calendario de partidos
- ✅ Estadísticas (goleadores, tarjetas, etc.)
- ✅ Gestión de licencias de jugadores
- ✅ Gestión de árbitros
- ✅ Sanciones disciplinarias
- ✅ Inscripción de equipos

### Para Clubes (intranet):
- ✅ Inscribir equipos y jugadores
- ✅ Ver plantillas
- ✅ Programar partidos (con 5 días de antelación)
- ✅ Consultar actas arbitrales
- ✅ Gestionar licencias
- ✅ Acceso a documentación oficial

### Módulos identificados (por URL):
- `NFG_CmpJornada` - Jornadas de competición
- `NFG_VisCompeticiones_Vis` - Visualización de competiciones
- `NFG_CMP_Goleadores` - Tabla de goleadores
- `NFG_PF_FAQ` - Portal federado FAQ

---

## 🚫 LIMITACIONES PARA WEB SCRAPING

### ❌ NO tiene API pública
- No existe documentación de API pública
- Solo intranets con login para clubes/federaciones
- Acceso controlado por credenciales

### ❌ Protecciones anti-scraping
- **Error 403 (Forbidden)** al intentar acceder vía scraping
- User-Agent verification
- Posibles tokens/sesiones requeridas
- WAF (Web Application Firewall) probable

### ❌ Estructura de URLs con parámetros opacos
```
?cod_primaria=1000120&CodCompeticion=12036&CodGrupo=49374&CodTemporada=18&CodJornada=27
```
- Códigos internos no documentados
- No es fácil construir URLs válidas sin conocer los códigos
- Los IDs parecen generados automáticamente por la BD

---

## 📊 ¿QUÉ LIGAS/COMPETICIONES GESTIONA?

Novanet gestiona competiciones de **TODAS las categorías** en las federaciones territoriales:

### Competiciones autonómicas/territoriales:
- ✅ **Primera Regional**
- ✅ **Segunda Regional**
- ✅ **Tercera Regional**
- ✅ **Preferente Autonómica**
- ✅ **Juvenil**
- ✅ **Cadete**
- ✅ **Infantil**
- ✅ **Fútbol Sala** (en algunas federaciones)

### Competiciones nacionales (coordina, pero no gestiona directamente):
- ⚠️ **3ª RFEF** - Coordinado por RFEF, datos pueden estar en Novanet de cada federación territorial
- ⚠️ **2ª RFEF** - Gestionado por RFEF
- ⚠️ **1ª RFEF** - Gestionado por RFEF

**IMPORTANTE:** Para 2ª RFEF, 1ª RFEF, no está claro si Novanet tiene los datos centralizados o si solo gestiona las categorías territoriales.

---

## 🎯 DATOS QUE PODRÍA TENER (SI FUERA ACCESIBLE)

Si tuviéramos acceso, Novanet probablemente tiene:

### Datos de jugadores:
- ✅ Nombre completo
- ✅ DNI/NIE (privado)
- ✅ Fecha de nacimiento / Edad
- ✅ Equipo actual
- ✅ Número de licencia
- ✅ Posición
- ✅ **Historial de licencias** (equipos anteriores)

### Estadísticas:
- ✅ Partidos jugados
- ✅ Goles
- ✅ Asistencias (si se registran)
- ✅ **Tarjetas amarillas**
- ✅ **Tarjetas rojas**
- ✅ **Sanciones** (partidos de suspensión)
- ❓ Minutos jugados (no confirmado)

### Datos de equipos:
- ✅ Plantilla completa
- ✅ Clasificación
- ✅ Resultados
- ✅ Calendario
- ✅ Actas de partidos

---

## 💡 ALTERNATIVAS PARA ACCEDER A DATOS

### OPCIÓN 1: Apps públicas de federaciones
Algunas federaciones tienen apps móviles que **podrían** tener datos públicos:
- **RFAF App** (Federación Asturiana) - Google Play Store
- Otras federaciones pueden tener apps similares

→ **Acción:** Investigar si las apps tienen APIs internas accesibles

### OPCIÓN 2: Páginas públicas de resultados
Aunque la intranet está protegida, algunas federaciones publican resultados en páginas web:
- **rffm.es** (Madrid)
- **asturfutbol.es** (Asturias)
- **ffcv.es** (Valencia)

→ **Acción:** Scrapear las páginas públicas de cada federación (no Novanet directo)

### OPCIÓN 3: Solicitar acceso oficial
- Contactar con federaciones territoriales
- Solicitar datos con fines de investigación/análisis
- Posible acceso si el proyecto es académico o sin ánimo de lucro

### OPCIÓN 4: Fuentes alternativas
Para categorías nacionales (2ª RFEF, 1ª RFEF), usar fuentes ya identificadas:
- **BeSoccer**
- **LaPreferente.com**
- **FutbolMe**
- **Transfermarkt** (ligas superiores)

---

## 🚦 CONCLUSIÓN Y RECOMENDACIÓN

### ❌ **Novanet NO ES VIABLE para scraping directo:**
1. Sistema interno con acceso restringido
2. Protecciones anti-scraping (403)
3. Sin API pública documentada
4. Requiere credenciales de club/federación

### ✅ **PARA CATEGORÍAS AUTONÓMICAS (Preferente, Regional, Juvenil):**
- Novanet es la **única fuente** de datos
- **Estrategia:** Scrapear páginas públicas de federaciones individuales (no Novanet directo)
- **Complejidad:** Alta (cada federación tiene estructura diferente)

### ✅ **PARA CATEGORÍAS NACIONALES (3ª RFEF, 2ª RFEF, 1ª RFEF):**
- **Usar fuentes alternativas ya validadas:**
  - BeSoccer (funcionando ✅)
  - LaPreferente
  - FutbolMe

---

## 📝 ACCIÓN RECOMENDADA

### **PARA EL PROYECTO IBERSCOUT:**

**NO incluir Novanet en Sprint 5-9.**

**Razones:**
1. Demasiada complejidad vs. beneficio
2. Riesgo legal (scraping de sistemas internos)
3. Protecciones técnicas difíciles de bypasear
4. Alternativas viables ya disponibles (BeSoccer, LaPreferente, FutbolMe)

**Si en el futuro queremos datos de categorías regionales/juveniles:**
- **Sprint 10+**: Investigar scraping de páginas públicas de federaciones individuales
- **Sprint 11+**: Considerar solicitar acceso oficial con fines de investigación

---

## 🔗 REFERENCIAS

- [Novanet - Artículo BeSoccer](https://es.besoccer.com/noticia/novanet-la-tecnologica-del-futbol-formativo-327747)
- [RFEF compra Novanet - 2Playbook](https://www.2playbook.com/mas-deporte/rfef-financia-con-recursos-uefa-compra-novanet-inyecta-125-millones-en-tecnologica_8473_102.html)
- [Manuales Clubes Novanet - FFCV](https://ffcv.es/wp/manuales-clubes-novanet/)
- [Novanet - Página oficial](https://www.novanet.es/)

---

**Última actualización:** 20 Noviembre 2025 - Sprint 5 Investigación
