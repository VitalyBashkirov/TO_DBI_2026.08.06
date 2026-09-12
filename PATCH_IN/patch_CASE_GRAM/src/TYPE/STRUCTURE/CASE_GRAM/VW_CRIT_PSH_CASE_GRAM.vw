class CASE_GRAM;

@name('[ПСБ] Простое представление')
view VW_CRIT_PSH_CASE_GRAM {
	type main is
		select A1(A1.[CODE] : C_CODE, A1.[NAME] : C_NAME) in ::[CASE_GRAM];
}
