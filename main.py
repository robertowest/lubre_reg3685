#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import datetime

def menu():
    """
    Función que limpia la pantalla y muestra nuevamente el menu
    """
    os.system('clear') # NOTA para windows tienes que cambiar clear por cls
    print("----------- LUBRE-----------------")
    print("1 - Compras")
    print("2 - Ventas")
    print("")
    # print("----------- DEBO -----------------")
    # print("x - Borrar tablas")
    # print("x - Cargar archivos de ventas")
    # print("x - Limpiar ventas y alícuotas")
    # print("x - Generar archivos de ventas")
    # print("")
    print("0 - Salir")
    print("")


if __name__ == "__main__":
    ANIO = int(input("Ingrese el año de procesamiento (%s) : " % datetime.datetime.now().year) or datetime.datetime.now().year)
    MES = int(input("Ingrese número de mes (%s) : " % datetime.datetime.now().month) or datetime.datetime.now().month)

    while True:
        # Mostramos el menu
        menu()

        # solicituamos una opción al usuario
        opcionMenu = input("Selecciona una opción >> ")

        if opcionMenu == "1":
            os.system('clear')
            from script.lubre import compras
            compras.procesar(ANIO, MES)

            # input("continuar ...")

        elif opcionMenu == "2":
            pass

        elif opcionMenu == "3":
            pass

        elif opcionMenu == "4":
            pass

        elif opcionMenu == "0":
            break

        else:
            print ("")
            input("Selecciona una opción válida...\npulsa una tecla para continuar")
