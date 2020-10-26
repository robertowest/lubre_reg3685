import csv, operator
import datetime

from script.comunes.progressbar import lines_in_file, update_progress
from script.afip.compras import Compras

RUTA = '/home/roberto/Programacion/python/reg3685'
ARCHIVO = RUTA + '/datos/lubre_compras.csv'
ARCH_COMPRA = RUTA + '/salida/lubre_01_compras.txt'
ARCH_ALICUOTA = RUTA + '/salida/lubre_02_compras_ali.txt'
LOG_ERROR = RUTA + '/salida/error.log'

def procesar(p_anio, p_mes):
    print("leyendo archivo lubre_compras.csv")
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
        # FECHA;TIPOCOMPROB;LETRA;TERMINAL;NUMERO;RAZON;IVA;CUIT;
        # GRAVADO;NOGRAVADO;IVA21;IVA10_5;PERC_IB;PERC_IVA;IVA27;TOTAL;
        # NETO;IDENC_MOV;IDPROVEDOR;IDFACPROVEDOR;IDPROVEDORTMP

        entrada = csv.DictReader(csvarchivo, delimiter=';', quoting=csv.QUOTE_NONE)
        for reg in entrada:
            try:
                if registro_valido(reg):
                    # comprobamos que la fecha sea válida y que esté en el mes correcto
                    reg['FECHA'] = str_to_date(reg['FECHA'], p_mes, p_anio)

                    compra = Compras(reg['FECHA'], 
                                     comprobante(reg['TIPOCOMPROB'] + reg['LETRA']), 
                                     reg['TERMINAL'], reg['NUMERO'])
                    compra.cuit = reg['CUIT']
                    compra.nombre = normalizar_texto(reg['RAZON'])
                    compra.gravado = reg['GRAVADO']
                    compra.no_gravado = reg['NOGRAVADO']
                    compra.iva21 = reg['IVA21']
                    compra.iva10 = reg['IVA10_5']
                    compra.iva27 = reg['IVA27']
                    compra.p_ibb = reg['PERC_IB']
                    compra.p_iva = reg['PERC_IVA']
                    compra.total = reg['TOTAL']

                    # recalculamos el registro
                    compra.recalcular()
                
                    file1.write(str(compra).replace('|', '') + '\n')
                    TOTAL += reg['TOTAL']
                    IVA += reg['IVA21'] + reg['IVA10_5'] + reg['IVA27']
                    for linea in compra.lineas_alicuotas():
                         file2.write(linea.replace('|', '') + '\n')
                else:
                    # raise Exception('registro inválido')
                    print('registro descartado')

            except Exception as e:
                log.write('IdFacProveedor %s - %s \n' % (reg['IDFACPROVEDOR'], str(e)))
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
    switcher = {
        'FACA': '001',
        'FACB': '006',
        'FACC': '011',
        'LSGA': '090',
        'NCRA': '003',
        'NCRB': '008',
        'NCRC': '013',
        'NDEA': '002',
        'NDEB': '007',
        'NDEC': '012',
    }
    return switcher.get(tipo, "FACA")        


def registro_valido(reg):
    # redondeamos los valores numéricos
    reg['IVA21'] = round(float(reg['IVA21'].replace(",",".")), 2)
    reg['IVA27'] = round(float(reg['IVA27'].replace(",",".")), 2)
    reg['IVA10_5'] = round(float(reg['IVA10_5'].replace(",",".")), 2)
    if (reg['IVA21'] + reg['IVA27'] + reg['IVA10_5']) == 0:
        return False

    # descartamos los comprobante que no sea de tipo A
    if reg['LETRA'] != 'A':
        # si tiene IVA ponemos letra A
        if (reg['IVA21'] + reg['IVA27'] + reg['IVA10_5']) != 0:
            reg['LETRA'] = 'A'
        else:
            return False

    reg['GRAVADO'] = round(float(reg['GRAVADO'].replace(",",".")), 2)
    reg['NOGRAVADO'] = round(float(reg['NOGRAVADO'].replace(",",".")), 2)
    reg['PERC_IB'] = round(float(reg['PERC_IB'].replace(",",".")), 2)
    reg['PERC_IVA'] = round(float(reg['PERC_IVA'].replace(",",".")), 2)
    reg['TOTAL'] = round(float(reg['TOTAL'].replace(",",".")), 2)

    return True


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

# if __name__ == "__main__":
#     procesar()
