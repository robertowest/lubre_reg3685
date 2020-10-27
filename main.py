#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import datetime

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


if __name__ == "__main__":
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
