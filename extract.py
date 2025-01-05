import pandas as pd
from umlsparser import UMLSParser

# 初始化 UMLSParser
umls = UMLSParser('../umls-extract')

procedures_path = "../医疗记录系统采集的各类信息/PROCEDURES_ICD.csv"
prescriptions_path = "../医疗记录系统采集的各类信息/PRESCRIPTIONS.csv"
diagnoses_path = "../医疗记录系统采集的各类信息/DIAGNOSES_ICD.csv"

# 处理code映射
def process_codes(codes, source_name, umls_parser):
    """
    :param codes: 待处理的代码列表
    :param source_name: UMLS数据集来源名称（例如 'ICD9CM', 'RXNORM'，'MMSL'）
    :param umls_parser: 已初始化的UMLSParser对象
    """
    for code in codes:
        for cui, concept in umls_parser.get_concepts().items():
            source_ids = concept.get_source_ids()
            if source_name in source_ids.keys():
                ids = source_ids.get(source_name)
                if code in ids:
                    tui = concept.get_tui()
                    name_of_semantic_type = umls_parser.get_semantic_types()[tui].get_name()
                    triples = umls_parser.get_concept_triples(cui)
                    print(f"Code: {code} (Source: {source_name})")
                    print(f"CUI: {cui}")
                    print(f"Name: {concept.get_preferred_names_for_language('ENG')[0]}")
                    print(f"Semantic Types: {name_of_semantic_type}")
                    for triple in triples:
                        print(f"CUI1: {triple[0]}, REL: {triple[1]}, CUI2: {triple[2]}")
                    print("-" * 50)

# 处理诊断/疾病
diagnoses_data = pd.read_csv(diagnoses_path)
diagnose_codes = diagnoses_data['ICD9_CODE'].astype(str).tolist()
print("Processing Diagnoses...")
process_codes(diagnose_codes,"ICD9CM", umls)

# 处理手术记录
#procedures_data = pd.read_csv(procedures_path)
#procedure_codes = procedures_data['ICD9_CODE'].astype(str).tolist()
#print("Processing Procedures...")
#process_codes(procedure_codes, "ICD9CM", umls)

# 处理处方用药
#prescriptions_data = pd.read_csv(prescriptions_path)
#ndc_codes = prescriptions_data['NDC'].astype(str).tolist()
#gsn_codes = prescriptions_data['GSN'].astype(str).tolist()

#print("Processing Prescriptions (NDC)...")
#process_codes(ndc_codes, "RXNORM", umls)

#print("Processing Prescriptions (GSN)...")
#process_codes(gsn_codes, "MMSL", umls)
