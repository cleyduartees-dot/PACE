# PACE — Quickstart

**Empieza en 2 minutos. No necesitas memorizar nada.**

PACE guarda la memoria de tu proyecto en un formato que cualquier IA puede leer,
para que nunca tengas que volver a explicar de qué se trata tu proyecto ni por qué
se tomó cada decisión.

---

## 1. Instalar

```
pip install pace-engine
```

Si no tienes Python, más abajo en la [guía completa](GUIA.md) te explicamos otras
opciones. Para comprobar que quedó:

```
pace --help
```

---

## 2. El único comando que necesitas recordar

```
pace
```

Escribe `pace` (sin nada más) y aparece un menú. Eliges un número y listo:

```
  PACE - que quieres hacer?

    1) Empezar / configurar la memoria de este proyecto
    2) Ver el estado del proyecto
    3) Guardar una nota
    4) Ver la memoria guardada
    5) Registrar una decision aprobada
    6) Comprobar que la memoria esta bien
    0) Salir

  Elige un numero >
```

Todo lo demás en PACE existe por si quieres ir más rápido con comandos directos,
pero **con el menú te alcanza para el día a día.**

---

## 3. Los primeros tres pasos

1. **Empieza la memoria del proyecto** — opción `1` del menú
   (o `pace init --guided .`). PACE te hace unas preguntas y crea la carpeta
   `.pace/` con lo esencial: qué es el proyecto, quién decide y qué falta.

2. **Guarda una nota cuando pase algo importante** — opción `3`
   (o `pace remember "lo que pasó"`). Así no se pierde en el chat.

3. **Cuando abras una IA nueva, dale el estado** — opción `2`
   (o `pace handoff .`). Copia lo que sale y pégalo: la IA ya sabe todo sin que
   tengas que reexplicar.

---

## 4. Comprueba que todo está sano

```
pace doctor
```

Si dice `VALID`, tu memoria está bien formada. Eso es todo lo que necesitas para
arrancar. Para el resto —decisiones, reglas, vigilancia automática, conectar tu
IA— mira la [guía completa](GUIA.md).
