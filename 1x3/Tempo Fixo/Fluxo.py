import xml.etree.ElementTree as ET
import os

def extract_max_flow(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    max_flow = 0
    for interval in root.findall('interval'):
        flow = float(interval.get('flow'))
        if flow > max_flow:
            max_flow = flow
    return max_flow

# Lista dos arquivos XML
file_names = [
    "detector_output_e1_t3_0.xml",
    "detector_output_e1_t3_1.xml",
    "detector_output_n1_t1_0.xml",
    "detector_output_n1_t1_1.xml",
    "detector_output_n2_t2_0.xml",
    "detector_output_n2_t2_1.xml",
    "detector_output_n3_t3_0.xml",
    "detector_output_n3_t3_1.xml",
    "detector_output_s1_t1_0.xml",
    "detector_output_s1_t1_1.xml",
    "detector_output_s2_t2_0.xml",
    "detector_output_s2_t2_1.xml",
    "detector_output_s3_t3_0.xml",
    "detector_output_s3_t3_1.xml",
    "detector_output_t1_n1_0.xml",
    "detector_output_t1_n1_1.xml",
    "detector_output_t1_s1_0.xml",
    "detector_output_t1_s1_1.xml",
    "detector_output_t1_t2_0.xml",
    "detector_output_t1_t2_1.xml",
    "detector_output_t1_w1_0.xml",
    "detector_output_t1_w1_1.xml",
    "detector_output_t2_n2_0.xml",
    "detector_output_t2_n2_1.xml",
    "detector_output_t2_s2_0.xml",
    "detector_output_t2_s2_1.xml",
    "detector_output_t2_t1_0.xml",
    "detector_output_t2_t1_1.xml",
    "detector_output_t2_t3_0.xml",
    "detector_output_t2_t3_1.xml",
    "detector_output_t3_e1_0.xml",
    "detector_output_t3_e1_1.xml",
    "detector_output_t3_n3_0.xml",
    "detector_output_t3_n3_1.xml",
    "detector_output_t3_s3_0.xml",
    "detector_output_t3_s3_1.xml",
    "detector_output_t3_t2_0.xml",
    "detector_output_t3_t2_1.xml",
    "detector_output_w1_t1_0.xml",
    "detector_output_w1_t1_1.xml"
]

# Dicionário para agrupar e armazenar o fluxo máximo de cada rua
grouped_files = {
    # Interseção t1
    "F1: w1_t1 t1_t2": ["detector_output_w1_t1_0.xml", "detector_output_w1_t1_1.xml", "detector_output_t1_t2_0.xml", "detector_output_t1_t2_1.xml"],
    "F2: t2_t1 t1_w1": ["detector_output_t2_t1_0.xml", "detector_output_t2_t1_1.xml", "detector_output_t1_w1_0.xml", "detector_output_t1_w1_1.xml"],
    "F3: s1_t1 t1_n1": ["detector_output_s1_t1_0.xml", "detector_output_s1_t1_1.xml", "detector_output_t1_n1_0.xml", "detector_output_t1_n1_1.xml"],
    "F4: n1_t1 t1_s1": ["detector_output_n1_t1_0.xml", "detector_output_n1_t1_1.xml", "detector_output_t1_s1_0.xml", "detector_output_t1_s1_1.xml"],
    # Interseção t2
    "F5: t1_t2 t2_t3": ["detector_output_t1_t2_0.xml", "detector_output_t1_t2_1.xml", "detector_output_t2_t3_0.xml", "detector_output_t2_t3_1.xml"],
    "F6: t3_t2 t2_t1": ["detector_output_t3_t2_0.xml", "detector_output_t3_t2_1.xml", "detector_output_t2_t1_0.xml", "detector_output_t2_t1_1.xml"],
    "F7: s2_t2 t2_n2": ["detector_output_s2_t2_0.xml", "detector_output_s2_t2_1.xml", "detector_output_t2_n2_0.xml", "detector_output_t2_n2_1.xml"],
    "F8: n2_t2 t2_s2": ["detector_output_n2_t2_0.xml", "detector_output_n2_t2_1.xml", "detector_output_t2_s2_0.xml", "detector_output_t2_s2_1.xml"],
    # Interseção t3
    "F9: t2_t3 t3_e1": ["detector_output_t2_t3_0.xml", "detector_output_t2_t3_1.xml", "detector_output_t3_e1_0.xml", "detector_output_t3_e1_1.xml"],
    "F10: e1_t3 t3_t2": ["detector_output_e1_t3_0.xml", "detector_output_e1_t3_1.xml", "detector_output_t3_t2_0.xml", "detector_output_t3_t2_1.xml"],
    "F11: s3_t3 t3_n3": ["detector_output_s3_t3_0.xml", "detector_output_s3_t3_1.xml", "detector_output_t3_n3_0.xml", "detector_output_t3_n3_1.xml"],
    "F12: n3_t3 t3_s3": ["detector_output_n3_t3_0.xml", "detector_output_n3_t3_1.xml", "detector_output_t3_s3_0.xml", "detector_output_t3_s3_1.xml"]
}

max_flows_grouped = {}

for group, files in grouped_files.items():
    max_flow = 0
    for file_name in files:
        file_path = file_name  # Arquivo está no mesmo diretório
        flow = extract_max_flow(file_path)
        if flow > max_flow:
            max_flow = flow
    max_flows_grouped[group] = max_flow

# Exibindo os resultados
for group, max_flow in max_flows_grouped.items():
    print(f'{group}: {max_flow}')
