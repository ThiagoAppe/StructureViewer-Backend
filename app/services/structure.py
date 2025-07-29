import requests
from bs4 import BeautifulSoup
import re

def GetStructure(articleCode: str):
    print(f"[DEBUG] Starting GetStructure for code: {articleCode}")

    url = f"http://192.168.0.2/reportes/estructura.php?art={articleCode}&herr=1"
    try:
        response = requests.get(url)
        response.encoding = 'utf-8'
        print(f"[DEBUG] HTTP status code: {response.status_code}")
        if response.status_code != 200:
            error_msg = f"HTTP Error: {response.status_code}"
            print(f"[ERROR] {error_msg}")
            return None, error_msg
    except Exception as e:
        print(f"[EXCEPTION] requests.get error: {e}")
        return None, str(e)

    soup = BeautifulSoup(response.text, "html.parser")
    rows = soup.find_all("tr")

    structure = []
    stack = []

    codePattern = re.compile(r"^(\d+)\s*(\.*)\s*([A-Z0-9\-\/]+)", re.I)

    for idx, row in enumerate(rows):
        cells = row.find_all("td")
        if not cells or not cells[0].text.strip():
            continue

        text1 = cells[0].get_text(strip=True).upper()
        match = codePattern.match(text1)

        if match:
            level = match.group(2).count(".")
            code = match.group(3)
            quantity = cells[1].get_text(strip=True) if len(cells) > 1 else ""
            description = cells[2].get_text(strip=True) if len(cells) > 2 else ""

            # Usar nombres de clave compatibles con el renderizador React
            node = {
                "codigo": code,
                "cantidad": quantity,
                "descripcion": description,
                "level": level,
                "hijos": []
            }

            while stack and stack[-1]["level"] >= level:
                stack.pop()

            if stack:
                stack[-1]["hijos"].append(node)
            else:
                structure.append(node)

            stack.append(node)
        else:
            print(f"[DEBUG] Row {idx} with text '{text1}' did not match pattern")

    # Validación para artículos vacíos
    if (
        len(structure) == 1 and
        structure[0]["codigo"] == articleCode and
        not structure[0]["descripcion"].strip()
    ):
        return None, "Code does not exist"

    return structure, None
