#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import os 
import shutil


def menu():
    """
    Función que limpia la pantalla y muestra nuevamente el menu
    """
    os.system('clear') # NOTA para windows tienes que cambiar clear por cls
    print("+---------- Menú ----------+")
    print("| 1 - Lubre Compras        |")
    print("| 2 - Lubre Ventas         |")
    print("| 3 - Debo  Compras        |")
    print("| 4 - Debo  Ventas         |")
    print("+--------------------------+")
    print("| 0 - Salir                |")
    print("+--------------------------+")

def eliminar_archivo(file_name):
    try:
        os.remove(file_name)
    except:
        pass

def vaciar_carpeta(folder_path):
    for root, dirs, files in os.walk(folder_path): 
        for f in files: 
            os.unlink(os.path.join(root, f)) 
        # for d in dirs: 
        #     shutil.rmtree(os.path.join(root, d))

def eliminar_carpeta(folder_path):
    for file_object in os.listdir(folder_path): 
        file_object_path = os.path.join(folder_path, file_object) 
        if os.path.isfile(file_object_path): 
            os.unlink(file_object_path) 
        else: 
            shutil.rmtree(file_object_path)


if __name__ == "__main__":
    # # eliminamos el contenido de los archivos
    # log = open(os.getcwd() + "/salida/error.log", 'w', newline='\r\n').close()
    # log = open(os.getcwd() + "/salida/resumen.txt", 'w', newline='\r\n').close()
    eliminar_archivo(os.getcwd() + "/salida/error.log")
    eliminar_archivo(os.getcwd() + "/salida/resumen.txt")
    vaciar_carpeta(os.getcwd() + "/salida/debo")
    vaciar_carpeta(os.getcwd() + "/salida/lubre")

    os.system('clear')
    ANIO = int(input("Ingrese el año de procesamiento (%s) : " % datetime.datetime.now().year) or datetime.datetime.now().year)
    MES = int(input("Ingrese número de mes (%s) : " % datetime.datetime.now().month) or datetime.datetime.now().month)

    while True:
        # Mostramos el menu
        menu()

        # solicituamos una opción al usuario
        opcionMenu = input("\nSelecciona una opción >> ")

        if opcionMenu == "1":
            os.system('clear')
            from script.lubre import compras
            compras.procesar(ANIO, MES)

            # input("continuar ...")

        elif opcionMenu == "2":
            os.system('clear')
            from script.lubre import ventas
            ventas.procesar(ANIO, MES)

        elif opcionMenu == "3":
            os.system('clear')
            from script.debo import compras
            compras.procesar(ANIO, MES)

        elif opcionMenu == "4":
            os.system('clear')
            from script.debo import ventas
            ventas.procesar(ANIO, MES)

        elif opcionMenu == "0":
            os.system('clear')
            break

        else:
            input("\nSelecciona una opción válida...\npulsa una tecla para continuar")
