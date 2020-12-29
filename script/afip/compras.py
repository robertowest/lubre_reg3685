from datetime import date, datetime
from dateutil.parser import *
from unidecode import unidecode

class Compras:
    def __init__(self, fecha, comprobante, terminal, numero, doc="80"):
        self.fecha = fecha
        self.comprobante = comprobante
        self.terminal = terminal
        self.numero = numero
        self.doc = doc
        self.cuit = ""
        self.nombre = ""
        self.gravado = 0
        self.no_gravado = 0
        self.iva21 = 0
        self.iva10 = 0
        self.iva27 = 0
        self.p_ibb = 0
        self.p_iva = 0
        self.itc = 0
        self.total = 0
        self.__alicuotas = 0
        self.cuit_emisor = ""
        self.nombre_emisor = ""

    def __str__(self):
        linea = [
            self.fecha,
            self.comprobante,
            self.terminal,
            self.numero,
            "".rjust(16, " "),      # despacho de importación
            self.doc,
            self.cuit,
            self.nombre,
            self.total,
            self.no_gravado,
            "0".rjust(15, "0"),     # importe de operaciones exentas
            "0".rjust(15, "0"),     # importe percepciones o pagos a cuenta del IVA
            "0".rjust(15, "0"),     # importe percepciones o pagos a cuenta de otros impuestos nacionales
            self.p_ibb,
            self.p_iva,
            self.itc,
            "PES",
            "0001000000",
            self.alicuotas,
            "0",                    # código de operación
            self.cfc,
            "0".rjust(15, "0"),     # otros tributos
            self.cuit_emisor,
            self.nombre_emisor,
            "0".rjust(15, "0")      # IVA comisión
        ]
        return "|".join(linea)

    @property
    def fecha(self):
        # if type(self.__fecha) is date:
        if isinstance(self.__fecha, (date, datetime)):
            return str(self.__fecha.strftime("%Y%m%d"))
        else:
            return "".join([x for x in self.__fecha if x.isdigit()])

    @fecha.setter
    def fecha(self, valor):
        if type(valor) is date or type(valor) is datetime :
            self.__fecha = valor
        elif type(parse(valor, dayfirst=True)) is datetime:
            self.__fecha = parse(valor, dayfirst=True, ignoretz=False).date()
        else:
            self.__fecha = date.today()

    @property
    def comprobante(self):
        return str(self.__comprobante).rjust(3, "0")

    @comprobante.setter
    def comprobante(self, valor):
        self.__comprobante = valor

    @property
    def terminal(self):
        if self.__terminal == "0":
            self.__terminal = "1"
        return str(self.__terminal).rjust(5, "0")

    @terminal.setter
    def terminal(self, valor):
        self.__terminal = valor

    @property
    def numero(self):
        return str(self.__numero).rjust(20, "0")

    @numero.setter
    def numero(self, valor):
        self.__numero = valor

    @property
    def doc(self):
        return self.__doc.rjust(2, "0")

    @doc.setter
    def doc(self, valor):
        self.__doc = valor[0:2].strip()

    @property
    def cuit(self):
        return self.__cuit.rjust(20, "0")

    @cuit.setter
    def cuit(self, valor):
        self.__cuit = valor[0:13].strip()

    @property
    def nombre(self):        
        return unidecode(self.__nombre).ljust(30, " ")

    @nombre.setter
    def nombre(self, valor):
        self.__nombre = valor[0:30]

    @property
    def gravado(self):
        return format(abs(self.__gravado), ".2f").replace(".", "").rjust(15, "0")

    @gravado.setter
    def gravado(self, valor):
        if type(valor) == str:
            self.__gravado = round(float(valor), 2)
        else:
            self.__gravado = round(valor, 2)

    @property
    def no_gravado(self):
        valor = format(abs(self.__no_gravado), ".2f").replace(".", "")
        if self.__no_gravado < 0 and self.__gravado > 0:
            signo = "-"
            largo = 14
        else:
            signo = ""
            largo = 15
        return signo + valor.rjust(largo, "0")

    @no_gravado.setter
    def no_gravado(self, valor):
        if type(valor) == str:
            self.__no_gravado = round(float(valor), 2)
        else:
            self.__no_gravado = round(valor, 2)

    @property
    def iva21(self):
        return format(abs(self.__iva21), ".2f").replace(".", "").rjust(15, "0")

    @iva21.setter
    def iva21(self, valor):
        if type(valor) == str:
            self.__iva21 = round(float(valor), 2)
        else:
            self.__iva21 = round(valor, 2)

    @property
    def iva10(self):
        return format(abs(self.__iva10), ".2f").replace(".", "").rjust(15, "0")

    @iva10.setter
    def iva10(self, valor):
        if type(valor) == str:
            self.__iva10 = round(float(valor), 2)
        else:
            self.__iva10 = round(valor, 2)

    @property
    def iva27(self):
        return format(abs(self.__iva27), ".2f").replace(".", "").rjust(15, "0")

    @iva27.setter
    def iva27(self, valor):
        if type(valor) == str:
            self.__iva27 = round(float(valor), 2)
        else:
            self.__iva27 = round(valor, 2)

    @property
    def p_ibb(self):
        return format(abs(self.__p_ibb), ".2f").replace(".", "").rjust(15, "0")

    @p_ibb.setter
    def p_ibb(self, valor):
        if type(valor) == str:
            self.__p_ibb = round(float(valor), 2)
        else:
            self.__p_ibb = round(valor, 2)

    @property
    def p_iva(self):
        return format(abs(self.__p_iva), ".2f").replace(".", "").rjust(15, "0")

    @p_iva.setter
    def p_iva(self, valor):
        if type(valor) == str:
            self.__p_iva = round(float(valor), 2)
        else:
            self.__p_iva = round(valor, 2)

    @property
    def itc(self):
        return format(abs(self.__itc), ".2f").replace(".", "").rjust(15, "0")

    @itc.setter
    def itc(self, valor):
        if type(valor) == str:
            self.__itc = round(float(valor), 2)
        else:
            self.__itc = round(valor, 2)

    @property
    def total(self):
        return format(abs(self.__total), ".2f").replace(".", "").rjust(15, "0")

    @total.setter
    def total(self, valor):
        if type(valor) == str:
            self.__total = round(float(valor), 2)
        else:
            self.__total = round(valor, 2)

    @property
    def alicuotas(self):
        self.__alicuotas = 0
        if self.__iva21 != 0:
            self.__alicuotas += 1
        if self.__iva10 != 0:
            self.__alicuotas += 1
        if self.__iva27 != 0:
            self.__alicuotas += 1
        return str(self.__alicuotas)

    @alicuotas.setter
    def alicuotas(self, valor):
        self.__alicuotas = valor

    @property
    def cfc(self):
        return format(abs(self.__cfc), ".2f").replace(".", "").rjust(15, "0")

    @cfc.setter
    def cfc(self, valor):
        if type(valor) == str:
            self.__cfc = round(float(valor), 2)
        else:
            self.__cfc = round(valor, 2)

    @property
    def cuit_emisor(self):
        if self.__comprobante == "060" and self.__cuit_emisor == "":
            self.__cuit_emisor = "30710051859"
        return self.__cuit_emisor.rjust(11, "0")

    @cuit_emisor.setter
    def cuit_emisor(self, valor):
        self.__cuit_emisor = valor[0:11].strip()

    @property
    def nombre_emisor(self):        
        if self.__comprobante == "060" and self.__nombre_emisor == "":
            self.__nombre_emisor = "LUBRE SRL"
        return unidecode(self.__nombre_emisor).ljust(30, " ")

    @nombre_emisor.setter
    def nombre_emisor(self, valor):
        self.__nombre_emisor = valor[0:30]


    # alicuotas
    def __define_linea_iva(self):
        return [
            self.comprobante,
            self.terminal,
            self.numero,
            self.doc,
            self.cuit
        ]

    def __valor_iva(self, iva, porcentaje, largo):
        neto = round(abs(iva) / porcentaje, 2)
        return format(neto, ".2f").replace(".", "").rjust(largo, "0")

    def lineas_alicuotas(self):
        lineas = []

        if self.__iva21 != 0:
            linea1 = self.__define_linea_iva()
            linea1.append(self.__valor_iva(self.__iva21, .21, 15))
            linea1.append("0005")
            linea1.append(self.iva21)
            lineas.append("|".join(linea1))

        if self.__iva10 != 0:
            linea2 = self.__define_linea_iva()
            linea2.append(self.__valor_iva(self.__iva10, .105, 15))
            linea2.append("0004")
            linea2.append(self.iva10)
            lineas.append("|".join(linea2))

        if self.__iva27 != 0:
            linea3 = self.__define_linea_iva()
            linea3.append(self.__valor_iva(self.__iva27, .27, 15))
            linea3.append("0006")
            linea3.append(self.iva27)
            lineas.append("|".join(linea3))

        return lineas


if __name__ == "__main__":
    c = Compras("1/3/20", "FACA", 101, 1245)
    c.cuit = "30710051859"
    c.nombre = "EDUARDO MARCELO ACUÑA"
    c.gravado = 27123.03
    c.iva21 = 4733.93
    c.iva10 = 1174.91
    c.iva27 = 0
    c.p_ibb = 474.65
    c.p_iva = 806.83
    c.total = 34313.35

    print( c )
    for linea in c.lineas_alicuotas():
        print( linea )
