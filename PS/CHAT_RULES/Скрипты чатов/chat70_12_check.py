import json, sys
J = r"F:\TO_DBI\DATA\Рубрикатор v5\4.RUBRICATOR_PROMPT v5.json"
data = json.load(open(J, encoding="utf-8"))
fs = data["rules"]["plpcheck.EXIST_ALL_OR_COLLECTIONS"]["regex_patterns"]["for_search"][0]["pattern"]
print("for_search[0].pattern = " + repr(fs))
print("total rules = " + str(len(data["rules"])))