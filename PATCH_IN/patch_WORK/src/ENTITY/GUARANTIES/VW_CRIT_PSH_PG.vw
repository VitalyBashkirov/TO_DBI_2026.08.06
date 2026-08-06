class GUARANTIES;

@count_collection(C_GR_RISK_HIST)
@count_collection(C_LIST_FACT)
@count_collection(C_PROPERTIES)
@name('[ПСБ] Портфель гарантий')
view VW_CRIT_PSH_PG {
	type main is
		select A1(
			[GUARANTIES].[Z1522841621].GetDateCalc : C_DATE_CALC,
			A1.[VNB_ACCOUNT]->(true)[MAIN_V_ID] : C_MAIN_V_ID,
			A1.[NUM_DOG] : C_NUM_DOG,
			A1.[PRINCIPAL]->(true)[NAME] : C_NAME,
			A1.[PRINCIPAL]->(true)[INN] : C_INN,
			A1.[SUMMA] : C_SUMMA,
			A1.[VALUTA]->(true)[CUR_SHORT] : C_CUR_SHORT,
			A1.[BENEFICIARY]->(true)[NAME] : C_NAME_1,
			[GUARANTIES].[PSH_L].GetPrc(A1%id) : PRC_ST,
			[GUARANTIES].[PSH_L].GetServiceQualSign(A1%id) : PRC_ST_1,
			[GUARANTIES].[PSH_L].GetPrcReserv(A1%id) : PRC_ST_2,
			[GUARANTIES].[PSH_L].GetSumCalcReserv(A1%id) : PRC_ST_3,
			[GUARANTIES].[PSH_L].GetResPortKindName(A1%id) : PRC_ST_4,
			[GUARANTIES].[PSH_L].GetSumZalog(A1%id) : PRC_ST_5,
			[GUARANTIES].[PSH_L].GetZalogName(A1%id) : PRC_ST_6,
			[GUARANTIES].[PSH_L].GetDateOutGua(A1%id) : PRC_ST_7,
			A1.[P_SROK].[NUM_INTERVALS] : C_P_SROK#NUM_INTERVALS,
			A1.[P_SROK].[UNIT_INTERVALS]->(true)[NAME] : C_NAME_3,
			A1.[DATE_ENDING] : C_DATE_ENDING,
			[GUARANTIES].[PSH_L].GETPROPVAL(A1%id, [GUARANTIES].[Z1522841621].GetDateCalc,
					1538896827) : C_PSB_DATE_END_MAIN_DOG,
			[GUARANTIES].[PSH_L].GetSumCom(A1%id) : SUM_COM,
			[GUARANTIES].[PSH_L].GetDaysDateEnd(A1%id) : DAYS,
			[GUARANTIES].[PSH_L].GetSumFactReserv(A1%id) : C_FACT_RES,
			A1.[COM_STATUS]->(true)[NAME] : C_NAME_2,
			A1.[DEPART]->(true)[CODE] : C_CODE,
			A1.[LIST_FACT] : C_LIST_FACT,
			A1.[GR_RISK_HIST] : C_GR_RISK_HIST,
			[GUARANTIES].[PSH_L].GETPROPVAL(A1%id, [GUARANTIES].[Z1522841621].GetDateCalc, 1563151603) : C_PSB_FZ,
			A1.[PROPERTIES] : C_PROPERTIES
		)
		in ::[GUARANTIES] all;
}
