import pandas as pd
from umlsparser import UMLSParser

# 初始化 UMLSParser
umls = UMLSParser('../umls-extract')

procedures_path = "../医疗记录系统采集的各类信息/PROCEDURES_ICD.csv"
drug_path = "../字典信息/D_MED.pkl"
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
                    # 提取三元组，其中rel可能是不具体的，比如AQ，RQ，PAR，这是因为umls中没有给出这两个概念的具体关系。
                    for triple in triples:
                        print(f"CUI1: {triple[0]}, REL: {triple[1]}, CUI2: {triple[2]}")
                    print("-" * 50)
# 三元组抽象关系解释
# PAR	Parent	CUI1概念是CUI2概念的子类
# CHD	Child	CUI2概念是CUI2概念的父类
# AQ	Allowed Qualifier	CUI1概念的修饰词关系
# RQ	Related or Synonym	CUI1概念与另一个概念相关（可为近义/狭义）

# 处理诊断/疾病
diagnoses_data = pd.read_csv(diagnoses_path)
diagnose_codes = diagnoses_data['ICD9_CODE'].astype(str).tolist()
print("Processing Diagnoses...")
process_codes(diagnose_codes,"ICD9CM", umls)

# 处理手术记录
procedures_data = pd.read_csv(procedures_path)
procedure_codes = procedures_data['ICD9_CODE'].astype(str).tolist()
print("Processing Procedures...")
process_codes(procedure_codes, "ICD9CM", umls)

# 处理药物
drug_data = pd.read_pickle(drug_path)
# 提取 ATC3 代码且去重
atc3_codes = drug_data['ATC3'].astype(str).drop_duplicates().tolist()
print("Processing Drugs(ATC3)...")
process_codes(atc3_codes, "ATC", umls)
