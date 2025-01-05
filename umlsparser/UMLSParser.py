import logging
import os
from typing import Dict

from tqdm import tqdm

from umlsparser.model.Concept import Concept
from umlsparser.model.SemanticType import SemanticType

UMLS_sources_by_language = {
    'ENG': ['MSH', 'CSP', 'NCI', 'PDQ', 'NCI_NCI-GLOSS', 'CHV', 'NCI_CRCH', 'NCI_CareLex', 'UWDA', 'FMA',
            'NCI_CDISC-GLOSS', 'NCI_NICHD', 'NCI_CTCAE', 'HPO', 'MEDLINEPLUS', 'NCI_CDISC', 'NCI_FDA', 'NCI_GAIA',
            'HL7V3.0', 'PSY', 'SPN', 'AIR', 'GO', 'CCC', 'SNOMEDCT_US', 'UMD', 'NIC', 'ALT', 'NCI_EDQM-HC', 'JABL',
            'NUCCPT', 'LNC', 'ICF-CY', 'NCI_BRIDG', 'ICF', 'NDFRT', 'NANDA-I', 'PNDS', 'NOC', 'OMS', 'NCI_CTEP-SDC',
            'NCI_DICOM', 'NCI_KEGG', 'NCI_BioC', 'MCM', 'AOT', 'NCI_CTCAE_5', 'NCI_CTCAE_3', 'MDR', 'NCI_INC'],
    'SPA': ['MDRSPA', 'SCTSPA', 'MSHSPA'],
    'FRE': ['MDRFRE', 'MSHFRE'],
    'JPN': ['MDRJPN'],
    'CZE': ['MDRCZE', 'MSHCZE'],
    'ITA': ['MDRITA'],
    'GER': ['MDRGER'],
    'POR': ['MDRPOR', 'MSHPOR'],
    'DUT': ['MDRDUT'],
    'HUN': ['MDRHUN'],
    'NOR': ['MSHNOR'],
    'HRV': ['MSHSCR']  # not sure
}

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class UMLSParser:

    def __init__(self, path: str, language_filter: list = []):
        """
        :param path: Basepath to UMLS data files
        :param languages: List of languages with three-letter style language codes (if empty, no filtering will be applied)
        """
        logger.info("Initialising UMLSParser for basepath {}".format(path))
        if language_filter:
            logger.info("Language filtering for {}".format(",".join(language_filter)))
        else:
            logger.info("No language filtering applied.")
        self.paths = {
            'MRCONSO': os.path.join(path, 'META', 'MRCONSO.RRF'),
            'MRDEF': os.path.join(path, 'META', 'MRDEF.RRF'),
            'MRSTY': os.path.join(path, 'META', 'MRSTY.RRF'),
            'SRDEF': os.path.join(path, 'NET', 'SRDEF'),
            'MRREL': os.path.join(path, 'META', 'MRREL.RRF'),
        }
        self.language_filter = language_filter
        self.concepts = {}
        self.relationships = {}
        self.semantic_types = {}
        self.__parse_mrconso__()
        self.__parse_mrdef__()
        self.__parse_mrsty__()
        self.__parse_srdef__()
        self.__parse_mrrel__()

    def __get_or_add_concept__(self, cui: str) -> Concept:
        concept = self.concepts.get(cui, Concept(cui))
        self.concepts[cui] = concept
        return concept

    def __get_or_add_semantic_type__(self, tui: str) -> SemanticType:
        semantic_type = self.semantic_types.get(tui, SemanticType(tui))
        self.semantic_types[tui] = semantic_type
        return semantic_type

    def __get_or_add_relationships__(self, cui: str) -> Concept:
        concept = self.concepts.get(cui, Concept(cui))
        self.concepts[cui] = concept
        return concept

    def __parse_mrrel__(self):
        """
        解析 MRREL.RRF 文件以提取概念之间的关系。
        """
        processed_relationships = set()
        for line in tqdm(open(self.paths['MRREL']), desc='Parsing UMLS relationships (MRREL.RRF)'):
            line = line.split('|')
            data = {
                'CUI1' : line[0],
                'CUI2' : line[4],
                'REL' : line[3],
                'RELA' : line[7]
            }

            # 使用一个元组来唯一标识关系
            unique_key = (data['CUI1'], data['CUI2'], data['REL'], data['RELA'])
            if unique_key not in processed_relationships:
                processed_relationships.add(unique_key)  # 添加到集合中

                # 添加关系到字典中
                cui1 = data['CUI1']
                if cui1 not in self.relationships:
                    self.relationships[cui1] = []
                self.relationships[cui1].append(data)

        logger.info('Parsed relationships for {} unique CUIs'.format(len(self.relationships.keys())))

    def __parse_mrconso__(self):
        for line in tqdm(open(self.paths['MRCONSO']), desc='Parsing UMLS concepts (MRCONSO.RRF)'):
            line = line.split('|')
            data = {
                'CUI': line[0],
                'LAT': line[1],  # language of term
                'TS': line[2],  # term status
                'LUI': line[3],
                'STT': line[4],
                'SUI': line[5],
                'ISPREF': line[6],
                'AUI': line[7],
                'SAUI': line[8],
                'SCUI': line[9],
                'SDUI': line[10],
                'SAB': line[11],  # source abbreviation
                'TTY': line[12],
                'CODE': line[13],  # Unique Identifier or code for string in source
                'STR': line[14],  # description string
                'SRL': line[15],
                'SUPPRESS': line[16],
                'CVF': line[17]
            }
            if len(self.language_filter) != 0 and data.get('LAT') not in self.language_filter:
                continue
            concept = self.__get_or_add_concept__(data.get('CUI'))
            concept.__add_mrconso_data__(data)
        logger.info('Found {} unique CUIs'.format(len(self.concepts.keys())))

    def __parse_mrdef__(self):
        source_filter = []
        for language in self.language_filter:
            for source in UMLS_sources_by_language.get(language):
                source_filter.append(source)

        for line in tqdm(open(self.paths['MRDEF']), desc='Parsing UMLS definitions (MRDEF.RRF)'):
            line = line.split('|')
            data = {
                'CUI': line[0],
                'AUI': line[1],
                'ATUI': line[2],
                'SATUI': line[3],
                'SAB': line[4],  # source
                'DEF': line[5],  # definition
                'SUPPRESS': line[6],
                'CVF': line[7]
            }
            if len(self.language_filter) != 0 and data.get('SAB') not in source_filter:
                continue
            concept = self.__get_or_add_concept__(data.get('CUI'))
            concept.__add_mrdef_data__(data)

    def __parse_mrsty__(self):
        for line in tqdm(open(self.paths['MRSTY']), desc='Parsing UMLS semantic types (MRSTY.RRF)'):
            line = line.split('|')
            data = {
                'CUI': line[0],
                'TUI': line[1],
                'STN': line[2],  # empty in MRSTY.RRF ?
                'STY': line[3],  # empty in MRSTY.RRF ?
                'ATUI': line[4],  # empty in MRSTY.RRF ?
                'CVF': line[5]  # empty in MRSTY.RRF ?
            }
            concept = self.__get_or_add_concept__(data.get('CUI'))
            concept.__add_mrsty_data__(data)

    def __parse_srdef__(self):
        for line in tqdm(open(self.paths['SRDEF']), desc='Parsing UMLS semantic net definitions (SRDEF)'):
            line = line.split('|')
            data = {
                'RT': line[0],  # Semantic Type (STY) or Relation (RL)
                'UI': line[1],  # Identifier
                'STY_RL': line[2],  # Name of STY / RL
                'STN_RTN': line[3],  # Tree Number of STY / RL
                'DEF': line[4],  # Definition of STY / RL
                'EX': line[5],  # Examples of Metathesaurus concepts
                'UN': line[6],  # Usage note for STY assignment
                'NH': line[7],  # STY and descendants allow the non-human flag
                'ABR': line[8],  # Abbreviation of STY / RL
                'RIN': line[9]  # Inverse of the RL
            }
            semantic_type = self.__get_or_add_semantic_type__(data['UI'])
            semantic_type.__add_srdef_data__(data)
        logger.info('Found {} unique TUIs'.format(len(self.semantic_types.keys())))

    def get_concepts(self) -> Dict[str, Concept]:
        """
        :return: A dictionary of all detected UMLS concepts with CUI being the key.
        """
        return self.concepts

    def get_semantic_types(self) -> Dict[str, SemanticType]:
        """
        :return: A dictionary of all detected UMLS semantic types with TUI being the key.
        """
        return self.semantic_types

    def get_concept_triples(self, cui: str):
        """
                获取给定 CUI 的所有关系三元组（CUI1, CUI2, REL/REL2）。

                :param cui: 概念的 CUI 标识符。
                :return: 一个关系三元组列表，包含 CUI1, CUI2, 和 REL/REL2。
                """
        if not hasattr(self, 'relationships'):
            logger.error("Relationships data not loaded. Ensure __parse_mrrel__ is called during initialization.")
            return []

        relationships = self.relationships.get(cui, [])
        triples = []

        for rel in relationships:
            rel_type = rel.get('RELA') if rel.get('RELA') else rel.get('REL')
            triples.append((cui, rel_type, rel['CUI2']))

        return triples

    def get_languages(self):
        return self.language_filter