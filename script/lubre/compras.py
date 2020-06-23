import csv, operator
import datetime

from script.comunes.progressbar import lines_in_file, update_progress
from script.afip import afip

RUTA = '/home/roberto/Programacion/python/reg3685'
ARCHIVO = RUTA + '/datos/lubre_compras.csv'
ARCH_COMPRA = RUTA + '/salida/lubre_01_compras.txt'
ARCH_ALICUOTA = RUTA + '/salida/lubre_02_compras_ali.txt'
ERROR = RUTA + '/salida/error.log'

def procesar(p_anio, p_mes):
    print("leyendo archivo compras_lubre.csv")
    open(ERROR, 'a').close()

    LINEAS = lines_in_file(ARCHIVO)
    LINEA = 0

    file1 = open(ARCH_COMPRA, 'w', encoding='ascii')
    file2 = open(ARCH_ALICUOTA, 'w', encoding='ascii')
    log = open(ERROR, 'w')

    with open(ARCHIVO, 'r', encoding='utf8') as csvarchivo:    
        # FECHA;TIPOCOMPROB;LETRA;TERMINAL;NUMERO;RAZON;IVA;CUIT;
        # GRAVADO;NOGRAVADO;IVA21;IVA10_5;PERC_IB;PERC_IVA;IVA27;TOTAL;
        # NETO;IDENC_MOV;IDPROVEDOR;IDFACPROVEDOR;IDPROVEDORTMP

        entrada = csv.DictReader(csvarchivo, delimiter=';', quoting=csv.QUOTE_NONE)
        for reg in entrada:
            try:
                # validaciones
                reg['IVA21'] = round(float(reg['IVA21'].replace(",",".")), 2)
                reg['IVA27'] = round(float(reg['IVA27'].replace(",",".")), 2)
                reg['IVA10_5'] = round(float(reg['IVA10_5'].replace(",",".")), 2)

                # sino tiene iva lo descartamos
                ALICUOTAS = 0
                if (reg['IVA21'] != 0):
                    ALICUOTAS += 1
                if (reg['IVA27'] != 0):
                    ALICUOTAS += 1
                if (reg['IVA10_5'] != 0):
                    ALICUOTAS += 1
                if ALICUOTAS == 0:
                    LINEA += 1
                    continue

                # redondeamos los valores
                reg['GRAVADO'] = round(float(reg['GRAVADO'].replace(",",".")), 2)
                reg['NOGRAVADO'] = round(float(reg['NOGRAVADO'].replace(",",".")), 2)
                reg['PERC_IB'] = round(float(reg['PERC_IB'].replace(",",".")), 2)
                reg['PERC_IVA'] = round(float(reg['PERC_IVA'].replace(",",".")), 2)
                reg['TOTAL'] = round(float(reg['TOTAL'].replace(",",".")), 2)

                # comprobamos que la fecha sea válida y que esté en el mes correcto
                reg['FECHA'] = str_to_date(reg['FECHA'], p_mes, p_anio)

                compra = afip.Compras(reg['FECHA'], reg['TIPOCOMPROB'] + reg['LETRA'], 
                                      reg['TERMINAL'], reg['NUMERO'])
                compra.cuit = reg['CUIT']
                compra.nombre = reg['RAZON']
                compra.neto = reg['GRAVADO']
                compra.no_gravado = reg['NOGRAVADO']
                compra.iva21 = reg['IVA21']
                compra.iva10 = reg['IVA10_5']
                compra.iva27 = reg['IVA27']
                compra.p_ibb = reg['PERC_IB']
                compra.p_iva = reg['PERC_IVA']
                compra.total = reg['TOTAL']
            
                file1.write(str(compra).replace('|', '') + '\n')
                for linea in compra.lineas_alicuotas():
                    file2.write(linea.replace('|', '') + '\n')

            except:
                log.write('Error al procesar la factura de compras Nº %s (%s)' % (reg['IDFACPROVEDOR'], reg['NUMERO']) + '\n')

            LINEA += 1
            update_progress("procesando ", LINEA/LINEAS)

    file1.close()
    file2.close()
    log.close()
    update_progress("procesando ", 1)


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
