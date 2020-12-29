import csv, operator
import datetime

from script.comunes.progressbar import lines_in_file, update_progress
from script.afip.compras import Compras

RUTA = '/home/roberto/Programacion/python/reg3685'
ARCHIVO = RUTA + '/datos/debo_compras.csv'
ARCH_COMPRA = RUTA + '/salida/debo_01_compras.txt'
ARCH_ALICUOTA = RUTA + '/salida/debo_02_compras_ali.txt'
LOG_ERROR = RUTA + '/salida/error.log'

def procesar(p_anio, p_mes):
    print("leyendo archivo debo_compras.csv")
    open(LOG_ERROR, 'a').close()

    LINEAS = lines_in_file(ARCHIVO)
    LINEA = 0
    TOTAL = 0
    IVA = 0
    ERRORES = 0
    AVISOS = 0

    file1 = open(ARCH_COMPRA, 'w', encoding='ascii', newline='\r\n')
    file2 = open(ARCH_ALICUOTA, 'w', encoding='ascii', newline='\r\n')
    log = open(LOG_ERROR, 'w', newline='\r\n')

    with open(ARCHIVO, 'r', encoding='utf8') as csvarchivo:
        # Fecha;TCO;N. Comprobante;Proveedor;CUIT;
        # Neto   ;N.Exento;IVA R.;IVA O.;IVA 10.5;IVA 27;IVA 5;IVA 2.5;
        # Imp. Int.;Ret. Gan.;Ret.I.Btos.;Per. IVA;Ret. IVA;
        # CNG;CNG 2;Per.I.Btos.;Ret.SUSS ;Ret.MUNI ;ARBA;DGR;CABA;PER. ARBA;PER. CABA;Dto.Pie(-);Per.MUNI ;Imp. Int. 2;
        # Total

        entrada = csv.DictReader(csvarchivo, delimiter=';', quoting=csv.QUOTE_NONE)
        for reg in entrada:
            try:
                if validar_registro(reg, p_mes, p_anio):
                    # Fecha, Tipo Comprobante + Letra, Terminal, Numero
                    # comprobante(reg['N. Comprobante'][0:3] + reg['N. Comprobante'][3:4]),
                    compra = Compras(reg['Fecha'], 
                                     comprobante(reg['TCO'] + reg['N. Comprobante'][3:4]),
                                     reg['N. Comprobante'][5:9],
                                     reg['N. Comprobante'][10:18])
                    compra.cuit = controlar_cuit(reg['CUIT'][3:16])
                    compra.nombre = normalizar_texto(reg['Proveedor'][6:36])
                    compra.gravado = reg['Neto   ']
                    compra.no_gravado = reg['N.Exento']
                    compra.iva21 = reg['IVA R.']
                    compra.iva10 = reg['IVA 10.5']
                    compra.iva27 = reg['IVA 27']
                    compra.p_ibb = reg['Per.I.Btos.']
                    compra.p_iva = reg['Per. IVA']
                    compra.itc = reg['Imp. Int.']
                    compra.total = reg['Total']
                    compra.cfc = reg['IVA R.'] + reg['IVA 10.5'] + reg['IVA 27']

                    file1.write(str(compra).replace('|', '') + '\n')
                    for linea in compra.lineas_alicuotas():
                            file2.write(linea.replace('|', '') + '\n')

                    IVA += reg['IVA R.'] + reg['IVA 10.5'] + reg['IVA 27']
                    TOTAL += reg['Total']

                else:
                    log.write('%s - registro inválido\n' % reg['N. Comprobante'])
                    AVISOS += 1

            except Exception as e:
                log.write('%s - %s \n' % 
                    (reg['N. Comprobante'], str(e))
                )
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

    else:
        if ERRORES == 1:
            print('\nSe encontró 1 error')
        else:
            print('\nSe encontraron {} errores'.format(ERRORES))
        print('Revise el log de errores {}'.format(LOG_ERROR))
    input("\nPulse [enter] tecla para continuar ...")


def validar_registro(reg, p_mes, p_anio):
    # comprobamos que la fecha sea válida y que esté en el mes correcto
    reg['Fecha'] = cadena_a_fecha(reg['Fecha'], p_mes, p_anio)

    # descartamos los comprobante que no sea de tipo A
    if reg['N. Comprobante'][3:4] != 'A':
        return False

    # redondeamos los valores numéricos
    reg['IVA R.']   = decimal(reg['IVA R.'])
    reg['IVA 27']   = decimal(reg['IVA 27'])
    reg['IVA 10.5'] = decimal(reg['IVA 10.5'])

    # descartamos los comprobante que no tienen IVA
    if (reg['IVA R.'] + reg['IVA 27'] + reg['IVA 10.5']) == 0:
        return False

    reg['Neto   ']     = decimal(reg['Neto   '])
    reg['N.Exento']    = decimal(reg['N.Exento'])
    reg['Per.I.Btos.'] = decimal(reg['Per.I.Btos.'])
    reg['Per. IVA']    = decimal(reg['Per. IVA'])
    reg['Imp. Int.']   = decimal(reg['Imp. Int.'])
    reg['Total']       = decimal(reg['Total'])

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


def comprobante(tipo):
    switcher = {
        "CIA": "111",
        "CIB": "222",
        "FTA": "001",
        "FTB": "006",
        "FTC": "011",
        "NDA": "002",
        "NDB": "007",
        "NDC": "012",
        "NCA": "003",
        "NCB": "008",
        "NCC": "013",
        "RER": "333",
        "TIA": "081",
        "TIB": "082",
    }
    return switcher.get(tipo, "FTA") 


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
    gravado    = round(reg['IVA R.'] / .21, 2) + \
                 round(reg['IVA 10.5'] / .105, 2) + \
                 round(reg['IVA 27'] / .27, 2)
    iva        = round(reg['IVA R.'] + reg['IVA 10.5'] + reg['IVA 27'], 2)
    otros      = round(reg['Per.I.Btos.'] + reg['Per. IVA'] + reg['Imp. Int.'])
    total      = round(reg['Total'], 2)
    no_gravado = round(total - (gravado + iva + otros), 2)

    if no_gravado != 0:
        if abs(no_gravado) > 1:
            reg['N.Exento'] = no_gravado
        else:
            # si son decimales los quitamos del gravado
            reg['Neto   '] = gravado - no_gravado
            reg['N.Exento'] = 0
