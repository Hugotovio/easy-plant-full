# validaciones.py
class Validaciones:

    @staticmethod
    def validate_tank_number(value):
        valid_tanks = ["smr-Tk-101", "smr-Tk-102", "smr-Tk-103", "smr-Tk-104", "ctg-tk-08", "ctg-tk-09", "ctg-tk-102", 
                       "baq-tk-504", "baq-tk-503", "baq-tk-505"]
        if value not in valid_tanks:
            raise ValueError("Número del tanque no válido.")
        return value

    @staticmethod
    def validate_float(value, field_name):
        try:
            return float(value)
        except ValueError:
            raise ValueError(f"{field_name} debe ser un número decimal.")

    @staticmethod
    def validate_api(api_value):
        # Asegúrate de que api_value es un número
        try:
            api_value = float(api_value)  # Convertimos el valor a float
        except ValueError:
            raise ValueError("El valor de API debe ser un número válido.")

        # Ahora puedes hacer la comparación
        if not (25 <= api_value <= 65):
            raise ValueError("El valor de API debe estar entre 25 y 65.")
        return api_value

    @staticmethod
    def validate_temperature(temp_value):
        try:
            temp_value = float(temp_value)  # Convertimos el valor a float
        except ValueError:
            raise ValueError("La temperatura debe ser un número válido.")

        if not (55 <= temp_value <= 100):
            raise ValueError("La temperatura debe estar entre 55 y 100 °F.")
        return temp_value
