import csv, operator
import datetime
import os

from script.comunes.progressbar import lines_in_file, update_progress
from script.afip.compras import Compras

RUTA = os.getcwd()
ARCHIVO = RUTA + '/datos/lubre_compras.csv'
ARCH_VENTA = RUTA + '/salida/lubre/compras.txt'
ARCH_ALICUOTA = RUTA + '/salida/lubre/compras_ali.txt'
LOG_ERROR = RUTA + '/salida/error.log'
RESUMEN = RUTA + '/salida/resumen.txt'

def procesar(p_anio, p_mes):
    print("leyendo archivo lubre_compras.csv")

    LINEAS = lines_in_file(ARCHIVO)
    LINEA = 0
    TOTAL = 0
    IVA = 0
    ERRORES = 0
    AVISOS = 0

    file1 = open(ARCH_VENTA, 'w', encoding='ascii', newline='\r\n')
    file2 = open(ARCH_ALICUOTA, 'w', encoding='ascii', newline='\r\n')
    log = open(LOG_ERROR, 'a', newline='\r\n')
    log.write("Lubre Compras -----------------------------------\n")

    with open(ARCHIVO, 'r', encoding='utf8') as csvarchivo:
        # FECHA;TIPOCOMPROB;LETRA;TERMINAL;NUMERO;RAZON;IVA;CUIT;
        # GRAVADO;NOGRAVADO;IVA21;IVA10_5;PERC_IB;PERC_IVA;IVA27;TOTAL;
        # NETO;IDENC_MOV;IDPROVEDOR;IDFACPROVEDOR;IDPROVEDORTMP

        entrada = csv.DictReader(csvarchivo, delimiter=';', quoting=csv.QUOTE_NONE)
        for reg in entrada:
            try:
                if validar_registro(reg, p_mes, p_anio):
                    compra = Compras(reg['FECHA'],
                                     comprobante(reg['TIPOCOMPROB'] + reg['LETRA']),
                                     reg['TERMINAL'], reg['NUMERO'])
                    compra.cuit = controlar_cuit(reg['CUIT'])
                    compra.nombre = normalizar_texto(reg['RAZON'])
                    compra.gravado = reg['GRAVADO']
                    compra.no_gravado = reg['NOGRAVADO']
                    compra.iva21 = reg['IVA21']
                    compra.iva10 = reg['IVA10_5']
                    compra.iva27 = reg['IVA27']
                    compra.p_ibb = reg['PERC_IB']
                    compra.p_iva = reg['PERC_IVA']
                    compra.total = reg['TOTAL']
                    compra.cfc = reg['IVA21'] + reg['IVA10_5'] + reg['IVA27']

                    file1.write(str(compra).replace('|', '') + '\n')
                    for linea in compra.lineas_alicuotas():
                         file2.write(linea.replace('|', '') + '\n')

                    IVA += reg['IVA21'] + reg['IVA10_5'] + reg['IVA27']
                    TOTAL += reg['TOTAL']

                else:
                    # raise Exception('registro inválido')
                    log.write("Línea {} - línea no procesada\n".format(LINEA+2))
                    AVISOS += 1

            except Exception as e:
                log.write("Línea {} ({}) - {}\n".format(LINEA+2, reg['IDFACPROVEDOR'], str(e)))
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
        log.write("Lubre Compras\n")
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


def comprobante(tipo):
    switcher = {
        "FACA": "001",
        "FACB": "006",
        "FACC": "011",
        "LSGA": "090",
        "LPRA": "060",
        "NCRA": "003",
        "NCRB": "008",
        "NCRC": "013",
        "NDEA": "002",
        "NDEB": "007",
        "NDEC": "012",
    }
    return switcher.get(tipo, "FACA")


def validar_registro(reg, p_mes, p_anio):
    # comprobamos que la fecha sea válida y que esté en el mes correcto
    reg['FECHA'] = cadena_a_fecha(reg['FECHA'], p_mes, p_anio)

    # redondeamos los valores numéricos
    reg['IVA21']   = decimal(reg['IVA21'])
    reg['IVA27']   = decimal(reg['IVA27'])
    reg['IVA10_5'] = decimal(reg['IVA10_5'])

    # descartamos los registros que no tienen IVA
    if (reg['IVA21'] + reg['IVA27'] + reg['IVA10_5']) == 0:
        return False

    # descartamos los comprobante que no sea de tipo A
    if reg['LETRA'] != 'A':
        # si tiene IVA ponemos letra A
        if (reg['IVA21'] + reg['IVA27'] + reg['IVA10_5']) != 0:
            reg['LETRA'] = 'A'
        else:
            return False

    reg['GRAVADO']   = decimal(reg['GRAVADO'])
    reg['NOGRAVADO'] = decimal(reg['NOGRAVADO'])
    reg['PERC_IB']   = decimal(reg['PERC_IB'])
    reg['PERC_IVA']  = decimal(reg['PERC_IVA'])
    reg['TOTAL']     = decimal(reg['TOTAL'])

    # if reg['GRAVADO'] != round((reg['IVA21'] / .21) + \
    #                            (reg['IVA27'] / .21) + \
    #                            (reg['IVA10_5'] / .105), 2):
    #     recalcular(reg)
    recalcular(reg)

    return True


def cadena_a_fecha(date_text, p_month, p_year):
    try:
        mydate = datetime.datetime.strptime(date_text, '%d/%m/%Y')
        if mydate.month != p_month:
            return datetime.date(p_year, p_month, 1)
        else:
            return mydate
    except ValueError:
        return datetime.date(p_year, p_month, 1)


def decimal(value):
    if value.strip() == '':
        value = 0
    if type(value) == str:
        value = float(value.replace(",","."))
    return round(value, 2)


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
        ("¥", " "),
    )
    for a, b in replacements:
        s = s.replace(a, b).replace(a.upper(), b.upper())
    return s


def recalcular(reg):
    # calculamos el gravado en función de los impuestos
    gravado    = round(reg['IVA21'] / .21, 2) + \
                 round(reg['IVA10_5'] / .105, 2) + \
                 round(reg['IVA27'] / .27, 2)
    iva        = round(reg['IVA21'] + reg['IVA10_5'] + reg['IVA27'], 2)
    otros      = round(reg['PERC_IB'] + reg['PERC_IVA'])
    total      = round(reg['TOTAL'], 2)
    no_gravado = round(total - (gravado + iva + otros), 2)

    if no_gravado != 0:
        if abs(no_gravado) > 1:
            reg['NOGRAVADO'] = no_gravado
        else:
            # si son decimales los quitamos del gravado
            reg['GRAVADO'] = gravado - no_gravado
            reg['NOGRAVADO'] = 0

