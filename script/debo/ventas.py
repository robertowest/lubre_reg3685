# debemos obtener el Libro IVA desde el botón [Libro]
#
import csv, operator
import datetime

from script.comunes.progressbar import lines_in_file, update_progress
from script.afip.ventas import Ventas

RUTA = '/home/roberto/Programacion/python/reg3685'
ARCHIVO = RUTA + '/datos/debo_ventas.csv'
ARCH_COMPRA = RUTA + '/salida/debo_03_ventas.txt'
ARCH_ALICUOTA = RUTA + '/salida/debo_04_ventas_ali.txt'
LOG_ERROR = RUTA + '/salida/error.log'

def procesar(p_anio, p_mes):
    print("leyendo archivo debo_ventas.csv")
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
        # Fecha;TCO;N. Comprobante;Cliente;CUIT;
        # Neto;IVA;Exento;IVA Otros;Percep;ImpInternos;ImpInt 1;
        # Redondeo;Perc. I.V.A.;Tasa Vial;IVA 105;Total

        entrada = csv.DictReader(csvarchivo, delimiter=';', quoting=csv.QUOTE_NONE)
        for reg in entrada:
            try:
                if (reg['Cliente'] != '**ANULADA**'):
                    if validar_registro(reg, p_anio, p_mes):
                        # fecha, tc + letra, terminal, numero
                        venta = Ventas(reg['Fecha'], 
                                       comprobante(reg['TCO'] + reg['N. Comprobante'][0:1]),
                                       reg['N. Comprobante'][2:6], 
                                       reg['N. Comprobante'][7:15])
                        venta.hasta = reg['N. Comprobante'][-8:]    # reg['N. Comprobante'][7:15]
                        venta.doc = reg['DOC']
                        venta.cuit = controlar_cuit(reg['CUIT'])
                        venta.nombre = normalizar_texto(reg['Cliente'])
                        venta.gravado = reg['Neto']   # + reg['Redondeo']
                        venta.no_gravado = reg['Exento']
                        venta.iva21 = reg['IVA']
                        venta.iva10 = reg['IVA 10.5']
                        venta.otro_iva = reg['IVA Otros']
                        venta.ii = reg['ImpInternos'] + reg['ImpInt 1']
                        venta.p_ibb = reg['Percep']
                        venta.p_iva = reg['Perc. I.V.A.']
                        venta.total = reg['Total']
                    
                        file1.write(str(venta).replace('|', '') + '\n')
                        for linea in venta.lineas_alicuotas():
                            file2.write(linea.replace('|', '') + '\n')

                        TOTAL += reg['Total']
                        IVA += reg['IVA'] + reg['IVA 10.5'] + reg['IVA Otros']

                    else:
                        log.write("Línea {} - línea no procesada\n".format(LINEA+2))
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
    swiiher = {
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
    return swiiher.get(tipo, "TIA")   


def validar_registro(reg, p_anio, p_mes):
    reg['DOC'] = "80"
    if reg['N. Comprobante'][:1] == "B":
        # corregimos los comprobantes duplicados, el listado de DEBO tiene errores al 
        # agrupar los comprobantes 
        desde = reg['N. Comprobante'][7:15]
        hasta = reg['N. Comprobante'][-8:]
        # if (int(hasta) - int(desde) > 500):
        #     reg['N. Comprobante'] = reg['N. Comprobante'].replace(desde, hasta)
        if desde == "00000002":
            reg['N. Comprobante'] = reg['N. Comprobante'].replace(desde, hasta)

        # definimos el tipo de DOC según corresponda
        if reg['CUIT'] == "" or reg['Cliente'] == "":
            if decimal(reg['Total']) > 1000:
                reg['DOC'] = "96"
                reg['CUIT'] = "12345678"
                reg['Cliente'] = "Consumidor Final"
            else:
                reg['DOC'] = "99"
                reg['Cliente'] = "Consumidor Final"

    # comprobamos que la fecha sea válida y que esté en el mes correcto
    reg['Fecha'] = cadena_a_fecha(reg['Fecha'][0:10], p_mes, p_anio)

    # redondeamos los valores
    reg['Neto']         = decimal(reg['Neto'])
    reg['Exento']       = decimal(reg['Exento'])
    reg['IVA']          = decimal(reg['IVA'])
    reg['IVA 10.5']     = decimal(reg['IVA 10.5'])
    reg['IVA Otros']    = decimal(reg['IVA Otros'])
    reg['ImpInternos']  = decimal(reg['ImpInternos'])
    reg['ImpInt 1']     = decimal(reg['ImpInt 1'])
    reg['Percep']       = decimal(reg['Percep'])
    reg['Perc. I.V.A.'] = decimal(reg['Perc. I.V.A.'])
    reg['Total']        = decimal(reg['Total'])

    # control de redondeo
    if reg['Neto'] != round((reg['IVA'] / .21) + (reg['IVA 10.5'] / .105), 2):
        # total = reg['Neto'] + reg['Exento'] + reg['IVA'] + reg['IVA 10.5'] + \
        #         reg['IVA Otros'] + reg['ImpInternos'] + reg['ImpInt 1'] + \
        #         reg['Percep'] + reg['Perc. I.V.A.']
        # if reg['Total'] != round(total, 2):
        recalcular(reg)

    # diferencia de totales
    if reg['Total'] != round(
        reg['Neto'] + reg['Exento'] + reg['IVA'] + 
        reg['IVA 10.5'] + reg['IVA Otros'] + 
        reg['ImpInternos'] + reg['ImpInt 1'] + 
        reg['Percep'] + reg['Perc. I.V.A.'], 2):
        recalcular(reg)

    return True


def decimal(value):
    if value.strip() == '':
        value = 0
    if type(value) == str:
        if "$" in value:
            value = float(value.replace("$", "").replace(".", "").replace(",","."))
        else:
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
    )
    for a, b in replacements:
        s = s.replace(a, b).replace(a.upper(), b.upper())
    return s


def recalcular(reg):
    # calculamos el gravado en función de los impuestos
    gravado = round((reg['IVA'] / .21) + \
                    (reg['IVA 10.5'] / .105), 2)
    iva = round(reg['IVA'] + reg['IVA 10.5'], 2)
    otros = round(reg['ImpInternos'] + reg['ImpInt 1'] + \
                  reg['Percep'] + reg['Perc. I.V.A.'] + \
                  reg['IVA Otros'], 2)
    total = reg['Total']
    no_gravado = round(total - (gravado + iva + otros), 2)

    if no_gravado != 0:
        reg['Neto'] = gravado
        reg['Exento'] = 0
        if abs(no_gravado) > 5:
            reg['Exento'] = no_gravado
        else:
            # si la diferencia es menor a 5, lo tratamos como redondeo
            reg['Total'] = round(total - no_gravado, 2)


# if __name__ == "__main__":
#     procesar()
