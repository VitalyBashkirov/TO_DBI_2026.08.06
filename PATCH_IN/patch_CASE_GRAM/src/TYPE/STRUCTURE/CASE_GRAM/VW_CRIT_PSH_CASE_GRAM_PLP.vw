class CASE_GRAM;

@access(used_to_set_rights:=true)
@name('[ПСБ] Полный список PL/Plus')
@tag('COPIED')
view VW_CRIT_PSH_CASE_GRAM_PLP {
	type main is
		select A1(A1.[CODE] : C_CODE, A1.[NAME] : C_NAME) in ::[CASE_GRAM];
}
