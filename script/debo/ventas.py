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

    file1 = open(ARCH_COMPRA, 'w', encoding='ascii', newline='\r\n')
    file2 = open(ARCH_ALICUOTA, 'w', encoding='ascii', newline='\r\n')
    log = open(LOG_ERROR, 'w', newline='\r\n')

    with open(ARCHIVO, 'r', encoding='utf8') as csvarchivo:
        # Fecha;TCO;N. Comprobante;Cliente;CUIT;
        # Neto;IVA;Exento;IVA Otros;Percep;ImpInternos;ImpInt 1;
        # Redondeo;Perc. I.V.A.;Tasa Vial;IVA 10.5;Total

        entrada = csv.DictReader(csvarchivo, delimiter=';', quoting=csv.QUOTE_NONE)
        for reg in entrada:
            try:
                if (reg['Cliente'] != '**ANULADA**'):
                    if registro_valido(reg, p_anio, p_mes):
                        # fecha, tc + letra, terminal, numero
                        venta = Ventas(reg['Fecha'], 
                                       comprobante(reg['TCO'] + reg['N. Comprobante'][0:1]),
                                       reg['N. Comprobante'][2:6], 
                                       reg['N. Comprobante'][7:15])
                        venta.hasta = reg['N. Comprobante'][-8:]
                        venta.doc = reg['DOC']
                        venta.cuit = reg['CUIT']
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
                        TOTAL += reg['Total']
                        IVA += reg['IVA'] + reg['IVA 10.5'] + reg['IVA Otros']
                        for linea in venta.lineas_alicuotas():
                            file2.write(linea.replace('|', '') + '\n')
                    else:
                        raise Exception('registro inválido')

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
    else:
        if ERRORES == 1:
            print('Se encontró 1 error')
        else:
            print('Se encontraron {} errores'.format(ERRORES))
        print('Revise el log de errores {}'.format(LOG_ERROR))
    input("Pulse [enter] tecla para continuar ...")


def str_to_date(date_text, p_month, p_year):
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
        'CIA': '111',
        'CIB': '222',
        'FTA': '001',
        'FTB': '006',
        'FTC': '011',
        'NDA': '002',
        'NDB': '007',
        'NDC': '012',
        'NCA': '003',
        'NCB': '008',
        'NCC': '013',
        'RER': '333',
        'TIA': '081',
        'TIB': '082',
    }
    return swiiher.get(tipo, "TIA")   


def registro_valido(reg, p_anio, p_mes):
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
            if convert_float(reg['Total']) > 1000:
                reg['DOC'] = "96"
                reg['CUIT'] = "12345678"
                reg['Cliente'] = "Consumidor Final"
            else:
                reg['DOC'] = "99"
                reg['Cliente'] = "Consumidor Final"

    # comprobamos que la fecha sea válida y que esté en el mes correcto
    reg['Fecha'] = str_to_date(reg['Fecha'][0:10], p_mes, p_anio)

    # redondeamos los valores
    reg['Neto']         = convert_float(reg['Neto'])
    reg['Exento']       = convert_float(reg['Exento'])
    reg['IVA']          = convert_float(reg['IVA'])
    reg['IVA 10.5']     = convert_float(reg['IVA 10.5'])
    reg['IVA Otros']    = convert_float(reg['IVA Otros'])
    reg['ImpInternos']  = convert_float(reg['ImpInternos'])
    reg['ImpInt 1']     = convert_float(reg['ImpInt 1'])
    reg['Redondeo']     = convert_float(reg['Redondeo'])
    reg['Percep']       = convert_float(reg['Percep'])
    reg['Perc. I.V.A.'] = convert_float(reg['Perc. I.V.A.'])
    reg['Total']        = convert_float(reg['Total'])

    # control de redondeo
    if reg['Neto'] != round((reg['IVA'] / .21) + (reg['IVA 10.5'] / .105), 2):
        # total = reg['Neto'] + reg['Exento'] + reg['IVA'] + reg['IVA 10.5'] + \
        #         reg['IVA Otros'] + reg['ImpInternos'] + reg['ImpInt 1'] + \
        #         reg['Percep'] + reg['Perc. I.V.A.']
        # if reg['Total'] != round(total, 2):
        recalcular(reg)

    return True


def convert_float(value):
    if value.strip() == '':
        value = 0
    if type(value) == str:
        value = float(value.replace(",","."))
    return round(value, 2)


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
        if abs(no_gravado) > 1:
            reg['Exento'] = no_gravado
        else:
            # si son decimales los quitamos del gravado
            reg['Total'] = round(total - no_gravado, 2)


# if __name__ == "__main__":
#     procesar()
