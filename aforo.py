import math
from datos import DataLoader 


class CalculadoraTanque:
    def __init__(self,altura_inicial,volumen_bruto_recibido,tanque):
        self.altura_inicial=altura_inicial
        self.volumen_bruto_recibido=volumen_bruto_recibido
        self.tanque=tanque
        

    def get_volumen_ctg(self, diccionario,n ):
        numero=int(n)     
        if numero == 0:
            return 0

        if str(numero) in diccionario:
            nr=numero/10
            parte_decimal, parte_entera = math.modf(nr)
            claves=[parte_entera,parte_decimal]
            

        if 11 <= numero <= 99:
            primer_digito = numero // 10
            segundo_digito = (numero % 10) / 10
            claves = [primer_digito, segundo_digito]

            suma = sum(diccionario.get(str(clave), 0) for clave in claves)
            return round(suma, 2)
        if 1 <= numero <= 9:
            primer_digito = numero / 10
            claves = [primer_digito]

            suma = sum(diccionario.get(str(clave), 0) for clave in claves)
            return round(suma, 2)

        claves = [math.floor(numero / 100) * 10]
        if numero >= 100:
            n = str(numero)
            claves.extend([int(n[2]), int(n[3]) / 10] if len(n) > 3 else [int(n[1]), int(n[2]) / 10])
        
        suma = sum(diccionario.get(str(clave), 0) for clave in claves)
        return round(suma, 2)



  

    

    import math

    def get_volumen_smr(self, diccionario, numero):
        n = float(numero)  # Convertir a float para manejar decimales
        print(n)
        
        # Definir listas de incremento para diferentes tanques
        increase_101 = [0.53, 0.67, 0.82, 0.97, 1.13, 1.30, 1.47, 1.66, 1.85]
        increase_102 = [0.54, 0.67, 0.80, 0.95, 1.09, 1.24, 1.40, 1.54, 1.75]
        increase_103 = [0.56, 0.69, 0.83, 0.97, 1.11, 1.26, 1.42, 1.59, 1.77]

        # Verificar si n está en el diccionario
        if str(n) in diccionario:
            return diccionario[str(n)]
        
        # Obtener parte entera y decimal
        parte_decimal, parte_entera = math.modf(n)
        parte_entera = int(parte_entera)

        # Obtener el valor base
        val_1 = diccionario.get(str(parte_entera), 0)

        # Inicializar val_2
        val_2 = 0

        # Determinar qué incremento aplicar basado en el tanque
        if "tk_101" in diccionario:
            index = int(parte_decimal * 10)
            if 0 <= index < len(increase_101):
                val_2 = increase_101[index]
        elif "tk_102" in diccionario:
            index = int(parte_decimal * 10)
            if 0 <= index < len(increase_102):
                val_2 = increase_102[index]
        elif "tk_103" in diccionario:
            index = int(parte_decimal * 10)
            if 0 <= index < len(increase_103):
                val_2 = increase_103[index]

        # Si n es un entero, retornar solo el valor base
        if parte_decimal == 0:
            return round(val_1, 2)

        # Retornar la suma redondeada de val_1 y val_2
        print(f"Valor Base: {val_1}, Incremento: {val_2}")  # Mensaje de depuración
        return round(val_1 + val_2, 2)

   






