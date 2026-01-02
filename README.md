# GHC
**Games Hour Counter**

App en segundo plano que registra el tiempo jugado a los videojuegos que tengas en tu lista!
Puedes visualizarlos y modificar la lista desde el Launcher

> [!CAUTION]
> Launcher solo para los más duros

***Requisitos***
- [ ] Python >3.8 (3.11 o 3.12 recomendado)
- [ ] Tener instaladas las dependencias de python de `requirements.txt`

> [!TIP]
> Para installar las dependencias puedes usar el comando `pip install -r requirements.txt`

***Como montar el programa***
1. Abre el archivo `builder.bat`
2. Abrir la carpeta creada llamada `dist`
3. Dentro de la carpeta copiar el archivo `games_hour_counter_tray.exe`
4. Pegarlo dentro de los programas de inicio: [How To](#como-agregar-un-programa-a-los-programas-de-inicio-en-windows).
5. Reiniciar Ordenador
6. Abrir el launcher creado en `/dist/games_hour_counter_launcher.exe`

> [!TIP]
> Puedes crear un acceso directo al launcher para abrirlo desde otro lugar

### Uso básico del launcher
Puedes agregar juegos para que se guarde el tiempo jugado.
Para hacerlo:
1. Click en `browse` y busque el .exe (Ejecutable del juego)
2. Introduzca en `Game Name` un friendly name para el juego
3. Click en `Add Game`

> [!IMPORTANT]
> Para que se guarde el tiempo jugado de los programas debes tener en segundo plano `games_hour_counter_tray.exe`
> Es por ello que lo agregamos a los programas de inicio, así cuando reiniciemos el ordenador se abrirá automáticamente


### Como agregar un programa a los programas de inicio en windows
Agregar un programa a los programas de inicio causa que, al encender el ordenador, se ejecute y se quede en segundo plano
Para ello:
1. Ejecutar el shortcut `Win+R`
2. Escribir `shell:startup` y abrir
3. Pegar el `games_hour_counter_tray.exe` o un acceso directo

> [!NOTE]
> Los programas de inicio están en %APP_DATA%/Roaming/Microsoft/Windows/Start Menu/Programs/Startup