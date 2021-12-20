import pandas as pd
 

def comprobar_cuit(cuits, ventas):
    '''
    Comprobamos que los CUIT sean correctos.
    A partir del listado 'cuits' se buscarán coincidencias en el archivo 'ventas'
    si las hay, serán reemplazados por el valor correcto.
    '''
    cuits = '/home/roberto/LubreSRL/Desarrollo/reg3685/datos/cuit_correccion.csv'
    ventas = '/home/roberto/LubreSRL/Desarrollo/reg3685/datos/debo_ventas.csv'
    cambios = 0

    df1 = pd.read_csv(cuits, delimiter=';')
    df2 = pd.read_csv(ventas, delimiter=';')

    for i in df1.index:
        df2.replace(to_replace=df1['CUIT'][i], value = df1['CORRECTO'][i], inplace = True)

    df2.to_csv('/home/roberto/LubreSRL/Desarrollo/reg3685/datos/debo_ventas2.csv', 
                sep=';', index=False)
    print( "Se grabó el archivo {} en la carpeta datos, recuerde renombrarlo antes de procesarlo.".format('debo_ventas2') )
    input( "Continuar ..." )
