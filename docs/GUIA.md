# Guía de uso de PACE

Esta guía te lleva de cero a dominar PACE, en lenguaje sencillo. No hace falta ser
programador para las partes básicas. Si solo quieres arrancar ya, mira primero el
[Quickstart](QUICKSTART.md) y vuelve aquí cuando quieras profundizar.

---

## ¿Qué es PACE y qué problema resuelve?

Cuando trabajas en un proyecto con una IA (o con varias personas), el contexto se
pierde: la IA olvida de qué iba el proyecto, por qué se decidió algo, quién manda,
o qué falta. Cada vez que abres un chat nuevo empiezas de cero.

PACE guarda todo eso en una carpeta llamada `.pace/` dentro de tu proyecto, en un
formato pensado para que **cualquier IA lo lea y lo entienda al instante**. Es la
memoria permanente del proyecto: la misión, las decisiones, las reglas, quién
decide y qué queda por hacer. En lugar de vivir en un chat que se borra, vive en tu
proyecto y se versiona con él.

La idea de fondo: **la IA propone, tú decides.** PACE deja por escrito quién es la
autoridad (el "ROOT_AUTHORITY") y hace que la IA consulte antes de cambiar cosas
importantes, en vez de inventar.

---

## Instalación

La forma normal:

```
pip install pace-engine
```

Comprueba que quedó bien:

```
pace --help
```

### Si te da un error de "externally managed environment"

Algunos sistemas (Linux modernos, Homebrew) bloquean `pip`. PACE lo sabe: su propio
comando de actualización usa el ajuste correcto automáticamente. Para instalar la
primera vez en esos entornos:

```
pip install pace-engine --break-system-packages
```

o, más recomendable, dentro de un entorno virtual:

```
python -m venv .venv && source .venv/bin/activate
pip install pace-engine
```

### Si no tienes Python

PACE está pensado para necesitar solo la librería estándar de Python, así que basta
con tener Python 3.10 o más. Un binario independiente (sin Python) está en el
roadmap pero aún no disponible.

---

## Lo único que de verdad tienes que recordar: `pace`

Escribe `pace` sin nada más y aparece un menú guiado. Eliges un número:

```
  PACE - que quieres hacer?

    1) Empezar / configurar la memoria de este proyecto
    2) Ver el estado del proyecto
    3) Guardar una nota
    4) Ver la memoria guardada
    5) Registrar una decision aprobada
    6) Comprobar que la memoria esta bien
    0) Salir
```

Cada opción es un atajo a un comando. Si algún día quieres ir más rápido, puedes
escribir los comandos directamente (abajo los tienes todos). Pero el menú te cubre
el uso diario sin memorizar nada.

> Nota: el menú aparece cuando corres `pace` en una terminal normal. En scripts o
> automatizaciones (sin terminal interactiva) `pace` muestra la ayuda, para no
> quedarse esperando.

---

## Los conceptos, en 30 segundos

- **`.pace/`** — la carpeta que PACE crea en tu proyecto. Ahí vive toda la memoria.
- **Handoff** — un resumen que PACE genera para que una IA se ponga al día al
  instante. Lo pegas al abrir un chat nuevo y la IA ya sabe todo.
- **Memoria de continuidad** — notas cortas que vas dejando ("pasó esto", "decidí
  aquello") para que nada se quede solo en el chat.
- **Decisiones y reglas** — acuerdos que quedan grabados y que la IA debe respetar.
- **ROOT_AUTHORITY** — la persona que decide. PACE lo deja por escrito.

---

## Guía por tareas (qué comando para qué)

### Empezar

- **Configurar la memoria de un proyecto que ya existe:**
  `pace init --guided .`
  Te hace preguntas y crea el `.pace/`. Si quieres además dejar tu nombre como
  autoridad: `pace init --owner "Tu Nombre" --owner-role "Presidente" .`

- **Que PACE lea tu proyecto y te proponga un borrador** (sin escribir nada):
  `pace discover .`
  Lee README, código y git y te propone qué poner en el `.pace/`. Tú confirmas.

- **Que PACE lea documentos** (notas, specs, PDFs) y te proponga lo que dedujo:
  `pace ingest ruta/al/documento`
  Tampoco escribe nada solo: propone, tú decides.

- **Crear un proyecto nuevo desde cero, ya gobernado por PACE:**
  `pace create`

### El día a día

- **Ver el estado del proyecto (el handoff):** `pace handoff .`
  Esto es lo que pegas cuando abres una IA nueva.

- **Guardar una nota:** `pace remember "lo que pasó"`

- **Ver la memoria guardada:** `pace recall`

- **Ver el contexto actual del proyecto:** `pace context`

### Dejar acuerdos por escrito

- **Registrar una decisión aprobada:** `pace capture "qué se decidió"`
  Para que la decisión no viva solo en el chat. Puedes añadir el porqué.

- **Registrar o listar reglas que la IA debe obedecer:** `pace rule`

### Actualizar la memoria sin romperla

- **Cambiar una sección protegida sin editar "a mano":** `pace supersede`
  PACE nunca edita en sitio: crea una versión nueva y marca la vieja como
  reemplazada. Así siempre hay historial.

- **Condensar notas viejas** para que el registro no crezca sin control (sin tirar
  nada): `pace condense`

### Que tu IA use PACE automáticamente

- **Conectar PACE con tu cliente de IA** (Claude Code, Cursor, AGENTS.md):
  `pace agent install`
  Deja configurado que la IA cargue el handoff sola, sin que tú hagas nada.

- **Verificación rápida por mensaje** (segura de correr siempre): `pace check`
  Responde: ¿PACE está aquí y al día?

### Vigilancia y salud

- **Comprobar que la memoria está bien formada:** `pace doctor`
  Si dice `VALID`, todo bien.

- **Vigilancia continua en segundo plano:** `pace watch`
  Avisa si hay deriva, algo roto, o una versión nueva del motor.

- **Guardián en cada commit de git:** `pace hook`
  Instala un pre-commit que bloquea commits que rompan el contrato.

- **Ver el roadmap como datos / detectar desajustes con tu gestor de tareas:**
  `pace roadmap`  (o `pace roadmap --against export.json`)

### Mantener PACE al día

- **Actualizar el propio PACE en un paso:** `pace update`
  Es el "presione aquí" del CLI. Cuando hay versión nueva, el handoff te avisa con
  el comando exacto.

---

## Un flujo completo de ejemplo

```
# 1. Entras a tu proyecto y creas la memoria
cd mi-proyecto
pace init --owner "Cley Duarte" --owner-role "Presidente" .

# 2. Trabajas... y cuando pasa algo importante, lo anotas
pace remember "Elegimos PostgreSQL sobre Mongo por las transacciones"
pace capture "Base de datos: PostgreSQL" --why "necesitamos transacciones ACID"

# 3. Abres una IA nueva y le das el estado
pace handoff .        # copias la salida y la pegas en el chat

# 4. De vez en cuando, revisas salud
pace doctor
```

---

## Preguntas frecuentes

**¿Mis datos salen a algún servidor?**
No. PACE trabaja con archivos locales dentro de tu proyecto. Todo se queda en tu
repositorio.

**¿Y si no quiero memorizar comandos?**
No los memorices. Escribe `pace` y usa el menú.

**¿PACE edita mis archivos sin permiso?**
Los comandos de lectura (`discover`, `ingest`, `check`, `doctor`, `recall`,
`handoff`, `context`, `roadmap`) no escriben nada: proponen o muestran. Los que
escriben lo hacen sobre la carpeta `.pace/`, y nunca editan en sitio las secciones
protegidas: crean versiones nuevas y conservan el historial.

**¿Cómo hago que mi IA respete las reglas?**
Corre `pace agent install` una vez. A partir de ahí tu cliente de IA carga el
handoff y las reglas por su cuenta.

**Tengo una versión vieja, ¿cómo actualizo?**
`pace update`. Y si estás en un entorno que bloquea pip, PACE ya usa el ajuste
correcto automáticamente.

---

¿Te falta algo en esta guía? Es parte del proyecto PACE y se puede mejorar como
cualquier otra cosa: propónlo y lo incorporamos.
