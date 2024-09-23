import math



class CalculadoraTanque:
    def __init__(self,altura_inicial,volumen_bruto_recibido,tanque):
        self.altura_inicial=altura_inicial
        self.volumen_bruto_recibido=volumen_bruto_recibido
        self.tanque=tanque
        

    def mostrar_volumen(self, diccionario,n ):
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




    def mostrar_altura(self, volume, aforo):
        aforo_tanque=self.preprocesar_datos(aforo)
        sorted_heights = sorted(aforo_tanque.keys())
        lower_height = None
        upper_height = None
        
        for i in range(len(sorted_heights) - 1):
            h1 = sorted_heights[i]
            h2 = sorted_heights[i + 1]
            
            v1 = aforo_tanque[h1]
            v2 = aforo_tanque[h2]
            
            if v1 <= volume <= v2:
                lower_height = h1
                upper_height = h2
                break  # Una vez encontrado el rango, podemos salir del bucle
        
        if lower_height is None or upper_height is None:
            return None  # El volumen está fuera del rango de datos
        
        v1 = aforo_tanque[lower_height]
        v2 = aforo_tanque[upper_height]
        
        height = lower_height + (volume - v1) * ((upper_height - lower_height) / (v2 - v1))
        
        return round(height * 10)
    def preprocesar_datos(self,aforo_tanque_json):
        """
        Convierte un diccionario JSON con claves en formato de cadena a claves numéricas (int o float).
        """
        aforo_tanque = {}
        for key, value in aforo_tanque_json.items():
            try:
                # Intenta convertir la clave a un número
                numeric_key = float(key)
                aforo_tanque[numeric_key] = value
            except ValueError:
                # Si no se puede convertir, maneja el error aquí
                print(f"Advertencia: La clave '{key}' no es un número válido y será ignorada.")
        return aforo_tanque




