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

    file1 = open(ARCH_COMPRA, 'w', encoding='ascii')
    file2 = open(ARCH_ALICUOTA, 'w', encoding='ascii')
    log = open(LOG_ERROR, 'w')

    with open(ARCHIVO, 'r', encoding='utf8') as csvarchivo:
        # Fecha;TCO;N. Comprobante;Proveedor;CUIT;
        # Neto   ;N.Exento;IVA R.;IVA O.;IVA 10.5;IVA 27;IVA 5;IVA 2.5;
        # Imp. Int.;Ret. Gan.;Ret.I.Btos.;Per. IVA;Ret. IVA;
        # CNG;CNG 2;Per.I.Btos.;Ret.SUSS ;Ret.MUNI ;ARBA;DGR;CABA;PER. ARBA;PER. CABA;Dto.Pie(-);Per.MUNI ;Imp. Int. 2;
        # Total

        entrada = csv.DictReader(csvarchivo, delimiter=';', quoting=csv.QUOTE_NONE)
        for reg in entrada:
            try:
                if registro_valido(reg):
                    # comprobamos que la fecha sea válida y que esté en el mes correcto
                    reg['Fecha'] = str_to_date(reg['Fecha'], p_mes, p_anio)

                    # Fecha, Tipo Comprobante + Letra, Terminal, Numero
                    compra = Compras(reg['Fecha'], 
                                     reg['N. Comprobante'][0:3] + reg['N. Comprobante'][3:4],
                                     reg['N. Comprobante'][5:9],
                                     reg['N. Comprobante'][10:18])
                    compra.cuit = reg['CUIT'][3:16]
                    compra.nombre = reg['Proveedor'][6:36]
                    compra.gravado = reg['Neto   ']
                    compra.no_gravado = reg['N.Exento']
                    compra.iva21 = reg['IVA R.']
                    compra.iva10 = reg['IVA 10.5']
                    compra.iva27 = reg['IVA 27']
                    compra.p_ibb = reg['Per.I.Btos.']
                    compra.p_iva = reg['Per. IVA']
                    compra.itc = reg['Imp. Int.']
                    compra.total = reg['Total']

                    # recalculamos el registro
                    compra.recalcular()
                
                    file1.write(str(compra).replace('|', '') + '\n')
                    TOTAL += reg['Total']
                    IVA += reg['IVA R.'] + reg['IVA 10.5'] + reg['IVA 27']
                    for linea in compra.lineas_alicuotas():
                            file2.write(linea.replace('|', '') + '\n')
                else:
                    # raise('Letra de comprobante distinto de A')
                    log.write('%s - %s \n' % 
                        (reg['N. Comprobante'], 'Letra de comprobante distinto de A')
                    )

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


def registro_valido(reg):
    # descartamos los comprobante que no sea de tipo A
    if reg['N. Comprobante'][3:4] != 'A':
        return False

    # redondeamos los valores numéricos
    reg['IVA R.'] = round(float(reg['IVA R.'].replace(",",".")), 2)
    reg['IVA 27'] = round(float(reg['IVA 27'].replace(",",".")), 2)
    reg['IVA 10.5'] = round(float(reg['IVA 10.5'].replace(",",".")), 2)
    if (reg['IVA R.'] + reg['IVA 27'] + reg['IVA 10.5']) == 0:
        return False

    reg['Neto   '] = round(float(reg['Neto   '].replace(",",".")), 2)
    reg['N.Exento'] = round(float(reg['N.Exento'].replace(",",".")), 2)
    reg['Per.I.Btos.'] = round(float(reg['Per.I.Btos.'].replace(",",".")), 2)
    reg['Per. IVA'] = round(float(reg['Per. IVA'].replace(",",".")), 2)
    reg['Imp. Int.'] = round(float(reg['Imp. Int.'].replace(",",".")), 2)
    reg['Total'] = round(float(reg['Total'].replace(",",".")), 2)

    return True


# if __name__ == "__main__":
#     procesar()
