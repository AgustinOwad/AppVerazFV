# sql_api.py
import requests

def consultar_deuda_historica(cuit):
    # Usamos la IP obtenida por nslookup: 45.235.97.44
    # Se debe incluir en las cabeceras el Host original
    url = f"https://45.235.97.44/CentralDeDeudores/v1.0/Deudas/Historicas/{cuit}"
    headers = {
         "Content-Type": "application/json",
         "Host": "api.bcra.gob.ar"
    }
    try:
        response = requests.get(url, headers=headers, verify=False, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("results", {})
    except Exception as e:
        return {"error": str(e)}
