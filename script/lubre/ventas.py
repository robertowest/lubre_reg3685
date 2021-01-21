import csv, operator
import datetime
import os

from script.comunes.progressbar import lines_in_file, update_progress
from script.afip.ventas import Ventas

RUTA = os.getcwd()
ARCHIVO = RUTA + '/datos/lubre_ventas.csv'
ARCH_COMPRA = RUTA + '/salida/lubre/ventas.txt'
ARCH_ALICUOTA = RUTA + '/salida/lubre/ventas_ali.txt'
LOG_ERROR = RUTA + '/salida/error.log'
RESUMEN = RUTA + '/salida/resumen.txt'

def procesar(p_anio, p_mes):
    print("leyendo archivo lubre_ventas.csv")

    LINEAS = lines_in_file(ARCHIVO)
    LINEA = 0
    TOTAL = 0
    IVA = 0
    ERRORES = 0
    AVISOS = 0

    file1 = open(ARCH_COMPRA, 'w', encoding='ascii', newline='\r\n')
    file2 = open(ARCH_ALICUOTA, 'w', encoding='ascii', newline='\r\n')
    log = open(LOG_ERROR, 'a', newline='\r\n')
    log.write("Lubre Ventas ------------------------------------\n")

    with open(ARCHIVO, 'r', encoding='utf8') as csvarchivo:
        # FECHA;TIPOCOMPROB;LETRA;TERMINAL;NUMERO;IVA;CUIT;NOMBRE;
        # NOGRAVA;GRAVADO;IVA21;OTROIVA;IMPINT;PERCIB;PERCIVA;TOTAL;
        # IVARNI;IVARI;IINT;PERCEP;PERCEP2;IDFACTURA

        entrada = csv.DictReader(csvarchivo, delimiter=';', quoting=csv.QUOTE_NONE)
        for reg in entrada:
            try:
                if validar_registro(reg, p_anio, p_mes):
                    venta = Ventas(reg['FECHA'], 
                                   comprobante(reg['TIPOCOMPROB'] + reg['LETRA']), 
                                   reg['TERMINAL'], reg['NUMERO'])
                    venta.cuit = controlar_cuit(reg['CUIT'])
                    venta.nombre = normalizar_texto(reg['NOMBRE'])
                    venta.gravado = reg['GRAVADO']
                    venta.no_gravado = reg['NOGRAVA']
                    venta.iva21 = reg['IVA21']
                    venta.iva10 = reg['OTROIVA']
                    venta.ii = reg['IMPINT']
                    venta.p_ibb = reg['PERCIB']
                    venta.p_iva = reg['PERCIVA']
                    venta.total = reg['TOTAL']
                
                    file1.write(str(venta).replace('|', '') + '\n')
                    for linea in venta.lineas_alicuotas():
                        file2.write(linea.replace('|', '') + '\n')

                    TOTAL += reg['TOTAL']
                    IVA += reg['IVA21'] + reg['OTROIVA']

                else:
                    # raise Exception('registro inválido')
                    log.write("Línea {} - línea no procesada\n".format(LINEA+2))
                    AVISOS += 1

            except Exception as e:
                log.write('IdFactura %s - %s \n' % (reg['IDFACTURA'], str(e)))
                ERRORES += 1

            LINEA += 1
            update_progress("procesando ", LINEA/LINEAS)

    file1.close()
    file2.close()
    log.close()
    update_progress("procesando ", 1)

    if ERRORES == 0:
        # '{:15,.2f}'.format(num).replace(',', '_').replace('.', ',').replace('_', '.')
        print('Total      : ' + '{:15,.2f}'.format(TOTAL))
        print('Total IVA  : ' + '{:15,.2f}'.format(IVA))
        if AVISOS != 0:
            print('\nExisten {} advertencias ({})'.format(AVISOS, LOG_ERROR))
        # agregamos información al resumen
        log = open(RESUMEN, 'a', newline='\r\n')
        log.write("Lubre Ventas\n")
        log.write("Total    :{:15,.2f}\n".format(TOTAL))
        log.write("Total IVA:{:15,.2f}\n".format(IVA))
        log.write("\n")
        log.close()
    else:
        if ERRORES == 1:
            print('\nSe encontró 1 error')
        else:
            print('\nSe encontraron {} errores'.format(ERRORES))
        print('Revise el log de errores {}'.format(LOG_ERROR))
    input("\nPulse [enter] tecla para continuar ...")


def validar_registro(reg, p_anio, p_mes):
    # comprobamos que la fecha sea válida y que esté en el mes correcto
    reg['FECHA'] = cadena_a_fecha(reg['FECHA'], p_mes, p_anio)

    # redondeamos los valores
    reg['GRAVADO'] = decimal(reg['GRAVADO'])
    reg['NOGRAVA'] = decimal(reg['NOGRAVA'])
    reg['IVA21']   = decimal(reg['IVA21'])
    reg['OTROIVA'] = decimal(reg['OTROIVA'])
    reg['IMPINT']  = decimal(reg['IMPINT'])
    reg['PERCIB']  = decimal(reg['PERCIB'])
    reg['PERCIVA'] = decimal(reg['PERCIVA'])
    reg['TOTAL']   = decimal(reg['TOTAL'])

    # comprobamos que no falte letra del comprobante
    if reg['LETRA'] == '':
        # si tiene IVA ponemos letra A
        reg['LETRA'] = ['A','C'][reg['IVA21'] + reg['OTROIVA'] == 0]

    if reg['GRAVADO'] != round((reg['IVA21'] / .21) + (reg['OTROIVA'] / .105), 2):
        recalcular(reg)

    return True


def decimal(value):
    if value.strip() == '':
        value = 0
    if type(value) == str:
        value = float(value.replace(",","."))
    return round(value, 2)


def cadena_a_fecha(date_text, p_month, p_year):
    try:
        mydate = datetime.datetime.strptime(date_text, '%d/%m/%Y')
        if mydate.month != p_month:
            return datetime.date(p_year, p_month, 1)
        else:
            return mydate
    except ValueError:
        return datetime.date(p_year, p_month, 1)


def comprobante(tipo):
    switcher = {
        "FACA": "001",
        "FACB": "006",
        "FACC": "011",
        "LSGA": "090",
        "LPRA": "003",
        "NCRA": "003",
        "NCRB": "008",
        "NCRC": "013",
        "NDEA": "002",
        "NDEB": "007",
        "NDEC": "012",
    }
    return switcher.get(tipo, "FACA")


def controlar_cuit(cuit):
    cuit = "".join([x for x in cuit if x.isdigit()])
    if cuit == "30710051859":   # si el CUIT es el de Lubre, lo cambiamos
        cuit = "20123456786"
    return cuit


def normalizar_texto(s):
    replacements = (
        ("á", "a"),
        ("é", "e"),
        ("í", "i"),
        ("ó", "o"),
        ("ú", "u"),
        ("ñ", "n"),
    )
    for a, b in replacements:
        s = s.replace(a, b).replace(a.upper(), b.upper())
    return s


def recalcular(reg):
    # calculamos el gravado en función de los impuestos
    gravado = round((reg['IVA21'] / .21) + \
                    (reg['OTROIVA'] / .105), 2)
    iva = round(reg['IVA21'] + reg['OTROIVA'], 2)
    otros = round(reg['IMPINT'] + reg['PERCIB'] + reg['PERCIVA'], 2)
    total = reg['TOTAL']
    no_gravado = round(total - (gravado + iva + otros), 2)

    if no_gravado != 0:
        reg['GRAVADO'] = gravado
        reg['NOGRAVA'] = 0
        if abs(no_gravado) > 1:
            reg['NOGRAVA'] = no_gravado
        else:
            # si son decimales los quitamos del gravado
            reg['TOTAL'] = round(total - no_gravado, 2)
