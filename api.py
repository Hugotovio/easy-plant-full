import pandas as pd
from datos import DataLoader

class ApiCorreccion:
    def __init__(self, api, temperatura):
        self.api = api
        self.temperatura = temperatura
        # Usa DataLoader para cargar datos JSON
        self.datos_loader = DataLoader(directory='.')
        self.tablas_api = self.datos_loader.load_file('api_observado.json')
        self.tablas_temp = self.datos_loader.load_file('temperaturas.json')

    def crear_matriz(self):
        # Usa DataLoader para cargar archivos CSV
        file_path_1 = 'api_corregido.csv'
        file_path_2 = 'factor_correccion.csv'
        
        # Verifica que los archivos CSV se cargan correctamente
        data1 = self.datos_loader.load_file(file_path_1)
        data2 = self.datos_loader.load_file(file_path_2)
        
        # Convertir los datos a DataFrames
        df1 = pd.DataFrame(data1)
        df2 = pd.DataFrame(data2)
        
        # Convertir los DataFrames a matrices (listas de listas)
        matrix_corregido = df1.values.tolist()
        matrix_factor_correccion = df2.values.tolist()
        
        return matrix_corregido, matrix_factor_correccion

    def encontrar_indices(self):
        # Convertir las claves de los JSON a enteros
        api_keys = {int(k): v for k, v in self.tablas_api.items()}
        temp_keys = {int(k): v for k, v in self.tablas_temp.items()}
        
        # Buscar la clave correspondiente al valor self.api
        key_api = next((k for k, v in api_keys.items() if v == self.api), None)
        # Buscar la clave correspondiente al valor self.temperatura
        key_tem = next((k for k, v in temp_keys.items() if v == self.temperatura), None)
        return key_api, key_tem
    
    def hallar_api_corregido(self, row_index, col_index, matrix):
        try:
            valor = matrix[row_index][col_index]
            return valor
        except IndexError:
            return "Índice fuera de rango"
    
    def hallar_factor_correccion(self, row_index, col_index, matrix):
        try:
            valor = matrix[row_index][col_index]
            return valor
        except IndexError:
            return "Índice fuera de rango"
    
    def encontrar_valor_mas_cercano(self, numero, lista):
        diferencia_minima = float('inf')
        valor_mas_cercano = None

        for valor in lista:
            diferencia = abs(float(numero) - float(valor))
            if diferencia < diferencia_minima:
                diferencia_minima = diferencia
                valor_mas_cercano = valor
        
        return valor_mas_cercano

    def corregir_correccion(self):
        matrix_api_corregido, matrix_factor_correccion = self.crear_matriz()
        api_indice, temperatura_indice = self.encontrar_indices()
        
        

        apicor = self.hallar_api_corregido(int(temperatura_indice) - 1, int(api_indice), matrix_api_corregido)
        
        api_aprox = self.encontrar_valor_mas_cercano(apicor, self.tablas_api.values())

        
        # Buscar la posición correspondiente al valor más cercano
        posicion = next((k for k, v in self.tablas_api.items() if v == api_aprox), None)

        
        # Convertir la posición a entero
        posicion = int(posicion)
        
        factor_correccion = self.hallar_factor_correccion(int(temperatura_indice) - 1, posicion, matrix_factor_correccion)

        fc=int(factor_correccion)/10000
        return apicor, fc

def main():
    # Instancia de ApiCorreccion
    api = 46  # Reemplaza con el valor real
    temperatura = 90  # Reemplaza con el valor real
    
    api_correccion = ApiCorreccion(api, temperatura)
    
    apicor, factor_correccion = api_correccion.corregir_correccion()
    
    
   


if __name__ == "__main__":
    main()
