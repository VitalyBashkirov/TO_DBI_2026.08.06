class AC_FIN;

@access_attribute(C_DEPART)
@name('[ПСХ] Среднедневные остатки 407-408 счетов куратора (с указанием периода)')
@tag('COPIED')
view VW_CRIT_PSH_SS_OST_PER_2 {
	type main is
		select A1(
			A1.[MAIN_V_ID] : C_MAIN_V_ID,
			A1.[DATE_OP] : C_DATE_OP,
			A1.[DATE_CLOSE] : C_DATE_CLOSE,
			A1.[FINTOOL]->(true, [FT_MONEY])[CUR_ISO]->(true)[INT_CUR_CODE] : C_INT_CUR_CODE,
			A1.[COM_STATUS]->(true)[NAME] : C_NAME_1,
			[AC_FIN].[Z1494265900].get_avg_saldo_v(A1%id) : C_SALDO,
			A1.[FINTOOL]->(true)[CUR_SHORT] : C_CUR_SHORT,
			[AC_FIN].[Z1494265900].get_avg_saldo_r(A1%id) : C_SALDO_1,
			A1.[NAME] : C_NAME,
			A1.[CLIENT_V]->(true)[NAME] : C_NAME_2,
			A1.[CLIENT_V]->(true)[INN] : C_INN,
			A1.[CLIENT_R]->(true)[NAME] : C_NAME_3,
			A1.[DEPART]->(true)[CODE] : C_CODE,
			A1.[DEPART] : C_DEPART,
			[AC_FIN].[Z1494265900].actual_accountant_name(A1%id, to_date(SYS_CONTEXT('IBS_USER', 'V_D_STOP'),
						'dd/mm/yyyy')) : C_ACTUAL_ACCOUNTANT_NAME
		)
		in ::[AC_FIN]
		where (SubStr(A1.[MAIN_V_ID], 1, 3) in (
				'407',
				'408'
			)
			and [AC_FIN].[Z1494265900].actual_accountant_name(A1%id, to_date(SYS_CONTEXT('IBS_USER', 'V_D_STOP'),
						'dd/mm/yyyy')) = stdlib.UserId.[NAME] /*'Куклинов Николай Станиславович'*/ );
}
