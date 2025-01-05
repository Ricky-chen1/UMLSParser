from umlsparser import UMLSParser
import collections

umls = UMLSParser('../umls-extract')
sources_counter = collections.defaultdict(int)
for cui, concept in umls.get_concepts().items():
    sources = concept.get_source_ids().keys()
    for source in sources:
        sources_counter[source] += 1
print('|SOURCE|COUNT|\n|------|-----|')
for source, count in sorted(sources_counter.items(), key=lambda t: t[1], reverse=True):
    print('|{}|{}|'.format(source, count))
