class Validaciones:
    
    @staticmethod
    def validate_tank_number(value):
        """Valida el número del tanque."""
        valid_tanks = ["smr-Tk-101", "smr-Tk-102", "smr-Tk-103", "smr-Tk-104", "ctg-tk-08", "ctg-tk-102", "ctg-tk-09"]
        if value not in valid_tanks:
            raise ValueError("Número del tanque no válido.")
        return value
    
    @staticmethod
    def validate_float(value, field_name):
        """Valida que un valor sea un número decimal y que no esté vacío."""
        if not value:
            raise ValueError(f"El campo {field_name} no puede estar vacío.")
        try:
            return float(value)
        except ValueError:
            raise ValueError(f"{field_name} debe ser un número decimal.")
    
    @staticmethod
    def validate_api(api_value):
        """Valida que el valor del API esté en el rango permitido."""
        if not api_value:
            raise ValueError("El campo API no puede estar vacío.")
        try:
            api_value = float(api_value)
        except ValueError:
            raise ValueError("El valor de API debe ser un número decimal.")
        if not (25 <= api_value <= 65):
            raise ValueError("El valor de API debe estar entre 25 y 65.")
        return api_value
    
    @staticmethod
    def validate_temperature(temperature_value):
        """Valida que la temperatura esté en el rango permitido."""
        if not temperature_value:
            raise ValueError("El campo Temperatura no puede estar vacío.")
        try:
            temperature_value = float(temperature_value)
        except ValueError:
            raise ValueError("La temperatura debe ser un número decimal.")
        if not (55 <= temperature_value <= 100):
            raise ValueError("La temperatura debe estar entre 55 y 100 °F.")
        return temperature_value
    
    @staticmethod
    def check_height_limits(numero, altura):
        """Lógica adicional para verificar límites de altura si aplica."""
        # Implementa la lógica si se requiere
        pass
