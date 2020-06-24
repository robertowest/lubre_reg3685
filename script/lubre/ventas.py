import csv, operator
import datetime

from script.comunes.progressbar import lines_in_file, update_progress
from script.afip.ventas import Ventas

RUTA = '/home/roberto/Programacion/python/reg3685'
ARCHIVO = RUTA + '/datos/lubre_ventas.csv'
ARCH_COMPRA = RUTA + '/salida/lubre_01_ventas.txt'
ARCH_ALICUOTA = RUTA + '/salida/lubre_02_ventas_ali.txt'
LOG_ERROR = RUTA + '/salida/error.log'

def procesar(p_anio, p_mes):
    print("leyendo archivo ventas_lubre.csv")
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
        # FECHA;TIPOCOMPROB;LETRA;TERMINAL;NUMERO;IVA;CUIT;NOMBRE;
        # NOGRAVA;GRAVADO;IVA21;OTROIVA;IMPINT;PERCIB;PERCIVA;TOTAL;
        # IVARNI;IVARI;IINT;PERCEP;PERCEP2;IDFACTURA

        entrada = csv.DictReader(csvarchivo, delimiter=';', quoting=csv.QUOTE_NONE)
        for reg in entrada:
            try:
                # comprobamos que la fecha sea válida y que esté en el mes correcto
                reg['FECHA'] = str_to_date(reg['FECHA'], p_mes, p_anio)
                # redondeamos los valores
                reg['GRAVADO'] = round(float(reg['GRAVADO'].replace(",",".")), 2)
                reg['NOGRAVA'] = round(float(reg['NOGRAVA'].replace(",",".")), 2)
                reg['IVA21'] = round(float(reg['IVA21'].replace(",",".")), 2)
                reg['OTROIVA'] = round(float(reg['OTROIVA'].replace(",",".")), 2)
                reg['IMPINT'] = round(float(reg['IMPINT'].replace(",",".")), 2)
                reg['PERCIB'] = round(float(reg['PERCIB'].replace(",",".")), 2)
                reg['PERCIVA'] = round(float(reg['PERCIVA'].replace(",",".")), 2)
                reg['TOTAL'] = round(float(reg['TOTAL'].replace(",",".")), 2)

                venta = Ventas(reg['FECHA'], reg['TIPOCOMPROB'] + reg['LETRA'], 
                               reg['TERMINAL'], reg['NUMERO'])
                venta.cuit = reg['CUIT']
                venta.nombre = reg['NOMBRE']
                venta.gravado = reg['GRAVADO']
                venta.no_gravado = reg['NOGRAVA']
                venta.iva21 = reg['IVA21']
                venta.otro_iva = reg['OTROIVA']
                venta.ii = reg['IMPINT']
                venta.p_ibb = reg['PERCIB']
                venta.p_iva = reg['PERCIVA']
                venta.total = reg['TOTAL']
            
                file1.write(str(venta).replace('|', '') + '\n')
                TOTAL += reg['TOTAL']
                for linea in venta.lineas_alicuotas():
                    file2.write(linea.replace('|', '') + '\n')
                    IVA += reg['IVA21']

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



# if __name__ == "__main__":
#     procesar()
