class AC_FIN;

@name('[ПСБ] Среднемесячные остатки 407-408 счетов ВСЕХ кураторов для EXCEL (с указанием периода)')
@tag('Task20190906')
view VW_CRIT_PSH_MON_AVER_TAIL {
	type main is
		select A1(
			A1.[CLIENT_V]->(true)[NAME] : C_NAME_2,
			A1.[CLIENT_V]->(true)[INN] : C_INN,
			A1.[DATE_OP] : C_DATE_OP,
			[AC_FIN].[PSH_AVG_MONTH_01].get_avg_saldo_r(A1%id) : C_SALDO_1,
			[AC_FIN].[Z1494265900].actual_accountant_name(A1%id, to_date(SYS_CONTEXT('IBS_USER', 'V_D_STOP'),
						'dd/mm/yyyy')) : C_ACTUAL_ACCOUNTANT_NAME
		)
		in ::[AC_FIN]
		where (SubStr(A1.[MAIN_V_ID], 1, 3) in (
				'407',
				'408'
			)
			and [AC_FIN].[PSH_AVG_MONTH_01].actual_accountant_name(A1%id, to_date(SYS_CONTEXT('IBS_USER', 'V_D_STOP'),
						'dd/mm/yyyy'))
is not null);
-- updated CHANGE_SHORT_NAME PSB_AVG_MONTH_01->PSH_AVG_MONTH_01 24/10/25
}
