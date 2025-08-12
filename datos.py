import json
import csv
import os

class DataLoader:
    def __init__(self, directory):
        self.directory = directory
    
    def load_file(self, filename):
        
        """
        Carga un archivo del directorio especificado y devuelve su contenido en
        una estructura de datos de Python. El archivo puede ser JSON o CSV.
        
        :param filename: Nombre del archivo a cargar.
        :return: Datos cargados del archivo.
        :raises FileNotFoundError: Si el archivo no se encuentra.
        :raises ValueError: Si el formato del archivo no es soportado.
        """
        file_path = os.path.join(self.directory, filename)
        
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"El archivo {filename} no se encuentra en el directorio especificado.")
        
        file_extension = filename.split('.')[-1].lower()
        
        if file_extension == 'json':
            return self._load_json(file_path)
        elif file_extension == 'csv':
            return self._load_csv(file_path)
        else:
            raise ValueError("Formato de archivo no soportado. Solo se permiten archivos JSON y CSV.")
    
    def _load_json(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _load_csv(self, file_path):
        data = []
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
        return data

