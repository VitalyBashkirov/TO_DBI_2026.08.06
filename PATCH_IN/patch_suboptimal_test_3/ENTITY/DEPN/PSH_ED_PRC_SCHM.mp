<?xml version="1.0" encoding="UTF-8"?>
<MethodPresentation classId="DEPN" formatVersion="1.2" shortName="PSH_ED_PRC_SCHM">
    <Properties>
        <Hotkey>Shift+P</Hotkey>
        <UserDriven>true</UserDriven>
        <ValidateOnLoadForm>ServerClient</ValidateOnLoadForm>
        <ValidateOnLostFocus>ServerClient</ValidateOnLostFocus>
    </Properties>
    <Parameters>
        <Parameter shortName="P_PRC_DOG">
            <ViewClassId>PRC_SCHEME</ViewClassId>
            <ViewFilter>UPPER({C_GROUP_CODE}) like 'DEP%'</ViewFilter>
            <ViewShortName>VW_CRIT_PRC_SCHEME</ViewShortName>
        </Parameter>
        <Parameter shortName="P_LAST_PRC">
            <ViewClassId>PRC_SCHEME</ViewClassId>
            <ViewFilter>UPPER({C_GROUP_CODE}) like 'DEP%'</ViewFilter>
            <ViewShortName>VW_CRIT_PRC_SCHEME</ViewShortName>
        </Parameter>
        <Parameter shortName="P_PENALTY_PRC">
            <ViewClassId>PRC_SCHEME</ViewClassId>
            <ViewFilter>UPPER({C_GROUP_CODE}) like 'DEP%'</ViewFilter>
            <ViewShortName>VW_CRIT_PRC_SCHEME</ViewShortName>
        </Parameter>
        <Parameter shortName="P_PRC_REG_RATE">
            <ViewClassId>PRC_SCHEME</ViewClassId>
            <ViewShortName>VW_CRIT_PRC_SCHEME</ViewShortName>
        </Parameter>
        <Parameter shortName="P_PRC_NALOG">
            <ViewClassId>PRC_SCHEME</ViewClassId>
            <ViewFilter>UPPER({C_GROUP_CODE}) like 'DEP%'</ViewFilter>
            <ViewShortName>VW_CRIT_PRC_SCHEME</ViewShortName>
        </Parameter>
    </Parameters>
    <Variables/>
    <Controls>
        <Form>
            <Properties>
                <Caption>Редактирование схем начисления %%[ПСБ]</Caption>
                <Height>211</Height>
                <ValidateName>Form1</ValidateName>
                <Width>739</Width>
            </Properties>
            <Controls>
                <Object>
                    <Properties>
                        <Caption>%% ставка по договору</Caption>
                        <ClassId>REF_PRC_SCH</ClassId>
                        <Height>24</Height>
                        <Left>8</Left>
                        <Qualifier>%PARAM%.P_PRC_DOG</Qualifier>
                        <TabIndex>1</TabIndex>
                        <Tips>Объект: Процентная ставка по договору</Tips>
                        <Top>36</Top>
                        <ValidateName>Object1</ValidateName>
                        <Width>216</Width>
                    </Properties>
                </Object>
                <Depend>
                    <Properties>
                        <ClassId>NAME</ClassId>
                        <Depend>%PARAM%.P_PRC_DOG</Depend>
                        <Height>24</Height>
                        <Left>230</Left>
                        <Qualifier>%PARAM%.P_PRC_DOG.NAME</Qualifier>
                        <TabIndex>2</TabIndex>
                        <Tips>Зависимость от объекта Процентная ставка по договору</Tips>
                        <Top>36</Top>
                        <ValidateName>Depend1</ValidateName>
                        <Width>273</Width>
                    </Properties>
                </Depend>
                <Object>
                    <Properties>
                        <Caption>%% ставка по истечении срока</Caption>
                        <ClassId>REF_PRC_SCH</ClassId>
                        <Height>24</Height>
                        <Left>8</Left>
                        <Qualifier>%PARAM%.P_LAST_PRC</Qualifier>
                        <TabIndex>5</TabIndex>
                        <Tips>Объект: Процентная ставка по истечении срока действия договора</Tips>
                        <Top>64</Top>
                        <ValidateName>Object2</ValidateName>
                        <Width>216</Width>
                    </Properties>
                </Object>
                <Depend>
                    <Properties>
                        <ClassId>NAME</ClassId>
                        <Depend>%PARAM%.P_LAST_PRC</Depend>
                        <Height>24</Height>
                        <Left>230</Left>
                        <Qualifier>%PARAM%.P_LAST_PRC.NAME</Qualifier>
                        <TabIndex>6</TabIndex>
                        <Tips>Зависимость от объекта Процентная ставка по истечении срока действия договора</Tips>
                        <Top>64</Top>
                        <ValidateName>Depend2</ValidateName>
                        <Width>273</Width>
                    </Properties>
                </Depend>
                <Object>
                    <Properties>
                        <Caption>%% ставка начисления по ЦБ</Caption>
                        <ClassId>REF_PRC_SCH</ClassId>
                        <Height>24</Height>
                        <Left>8</Left>
                        <Qualifier>%PARAM%.P_PRC_REG_RATE</Qualifier>
                        <TabIndex>9</TabIndex>
                        <Tips>Объект: Процентная ставка начисления по ставке ЦБ</Tips>
                        <Top>120</Top>
                        <ValidateName>Object3</ValidateName>
                        <Width>216</Width>
                    </Properties>
                </Object>
                <Depend>
                    <Properties>
                        <ClassId>NAME</ClassId>
                        <Depend>%PARAM%.P_PRC_REG_RATE</Depend>
                        <Height>24</Height>
                        <Left>230</Left>
                        <Qualifier>%PARAM%.P_PRC_REG_RATE.NAME</Qualifier>
                        <TabIndex>10</TabIndex>
                        <Tips>Зависимость от объекта Процентная ставка начисления по ставке ЦБ</Tips>
                        <Top>120</Top>
                        <ValidateName>Depend3</ValidateName>
                        <Width>273</Width>
                    </Properties>
                </Depend>
                <Object>
                    <Properties>
                        <Caption>%% ставка начисления налога</Caption>
                        <ClassId>REF_PRC_SCH</ClassId>
                        <Height>24</Height>
                        <Left>8</Left>
                        <Qualifier>%PARAM%.P_PRC_NALOG</Qualifier>
                        <TabIndex>12</TabIndex>
                        <Tips>Объект: Процентная ставка начисления налога на доходы</Tips>
                        <Top>148</Top>
                        <ValidateName>Object4</ValidateName>
                        <Width>216</Width>
                    </Properties>
                </Object>
                <Depend>
                    <Properties>
                        <ClassId>NAME</ClassId>
                        <Depend>%PARAM%.P_PRC_NALOG</Depend>
                        <Height>24</Height>
                        <Left>230</Left>
                        <Qualifier>%PARAM%.P_PRC_NALOG.NAME</Qualifier>
                        <TabIndex>13</TabIndex>
                        <Tips>Зависимость от объекта Процентная ставка начисления налога на доходы</Tips>
                        <Top>148</Top>
                        <ValidateName>Depend4</ValidateName>
                        <Width>273</Width>
                    </Properties>
                </Depend>
                <Button>
                    <Properties>
                        <Caption>OK</Caption>
                        <Height>24</Height>
                        <Left>431</Left>
                        <Qualifier>OK</Qualifier>
                        <TabIndex>15</TabIndex>
                        <Tips>Выполнить метод</Tips>
                        <Top>180</Top>
                        <ValidateName>OK</ValidateName>
                        <Width>144</Width>
                    </Properties>
                </Button>
                <Button>
                    <Properties>
                        <Caption>Отмена</Caption>
                        <Height>24</Height>
                        <Left>583</Left>
                        <Qualifier>CANCEL</Qualifier>
                        <TabIndex>16</TabIndex>
                        <Tips>Отказ от выполнения</Tips>
                        <Top>180</Top>
                        <ValidateName>CANCEL</ValidateName>
                        <Width>144</Width>
                    </Properties>
                </Button>
                <Object>
                    <Properties>
                        <Caption>%% ставка при расторжении</Caption>
                        <ClassId>REF_PRC_SCH</ClassId>
                        <Height>24</Height>
                        <Left>8</Left>
                        <Qualifier>%PARAM%.P_PENALTY_PRC</Qualifier>
                        <TabIndex>8</TabIndex>
                        <Tips>Объект:Штрафная процентная ставка</Tips>
                        <Top>92</Top>
                        <ValidateName>Object5</ValidateName>
                        <Width>216</Width>
                    </Properties>
                </Object>
                <Text>
                    <Properties>
                        <ClassId>NAME</ClassId>
                        <Depend>%PARAM%.P_PENALTY_PRC</Depend>
                        <Height>24</Height>
                        <Left>230</Left>
                        <Qualifier>%PARAM%.P_PENALTY_PRC.NAME</Qualifier>
                        <TabIndex>7</TabIndex>
                        <Tips>Наименование</Tips>
                        <Top>91</Top>
                        <ValidateName>Text1</ValidateName>
                        <Width>273</Width>
                    </Properties>
                </Text>
                <Array>
                    <Properties>
                        <Caption>Журнал начисленных %%</Caption>
                        <ClassId>JOUR_CALC_PRC</ClassId>
                        <Height>56</Height>
                        <Left>508</Left>
                        <Qualifier>%VAR%.V_JOUR_CALC_PRC</Qualifier>
                        <TabIndex>4</TabIndex>
                        <Tips>Массив: Журнал начисленных процентов</Tips>
                        <Top>60</Top>
                        <ValidateName>Array5</ValidateName>
                        <Width>220</Width>
                        <Zorder>-1</Zorder>
                    </Properties>
                </Array>
                <Array>
                    <Properties>
                        <Caption>Журнал начисленных %% по ЦБ</Caption>
                        <ClassId>JOUR_CALC_PRC</ClassId>
                        <Height>24</Height>
                        <Left>508</Left>
                        <Qualifier>%VAR%.V_JOUR_CB_PRC</Qualifier>
                        <TabIndex>11</TabIndex>
                        <Tips>Массив: Журнал %% по ставке ЦБ</Tips>
                        <Top>120</Top>
                        <ValidateName>Array7</ValidateName>
                        <Width>220</Width>
                        <Zorder>-2</Zorder>
                    </Properties>
                </Array>
                <Array>
                    <Properties>
                        <Caption>Журнал рассчитанного налога</Caption>
                        <ClassId>JOUR_CALC_PRC</ClassId>
                        <Height>24</Height>
                        <Left>508</Left>
                        <Qualifier>%VAR%.V_JOUR_PRC_TAX</Qualifier>
                        <TabIndex>14</TabIndex>
                        <Tips>Массив: Журнал рассчитанного налога на %%</Tips>
                        <Top>148</Top>
                        <ValidateName>Array8</ValidateName>
                        <Width>220</Width>
                        <Zorder>-3</Zorder>
                    </Properties>
                </Array>
                <Check>
                    <Properties>
                        <Caption>Сохранить в историю</Caption>
                        <ClassId>BOOLEAN</ClassId>
                        <Height>16</Height>
                        <Left>508</Left>
                        <Qualifier>%PARAM%.P_SAVE_CHANGE</Qualifier>
                        <TabIndex>3</TabIndex>
                        <Tips>Логическое значение (Сохранить изменение Основной схемы)</Tips>
                        <Top>36</Top>
                        <ValidateName>Check1</ValidateName>
                        <Width>164</Width>
                    </Properties>
                </Check>
                <Label>
                    <Properties>
                        <Caption>Дата изменения</Caption>
                        <Height>24</Height>
                        <Left>8</Left>
                        <Qualifier>%PARAM%.P_DATE</Qualifier>
                        <TabIndex>0</TabIndex>
                        <Tips>Поясняющая надпись (Дата изменения)</Tips>
                        <Top>8</Top>
                        <ValidateName>Label1</ValidateName>
                        <Width>216</Width>
                    </Properties>
                </Label>
                <Date>
                    <Properties>
                        <ClassId>DATE</ClassId>
                        <Left>228</Left>
                        <Qualifier>%PARAM%.P_DATE</Qualifier>
                        <TabIndex>0</TabIndex>
                        <Tips>Дата изменения</Tips>
                        <Top>8</Top>
                        <ValidateName>Date1</ValidateName>
                    </Properties>
                </Date>
                <Text>
                    <Properties>
                        <ClassId>STRING_32000</ClassId>
                        <Height>24</Height>
                        <Left>681</Left>
                        <Qualifier>%VAR%.V_DEST_STR</Qualifier>
                        <TabIndex>69</TabIndex>
                        <Tips>Строка валидатора</Tips>
                        <Top>7</Top>
                        <ValidateName>V_DEST_STR</ValidateName>
                        <Visible>false</Visible>
                        <Width>27</Width>
                    </Properties>
                </Text>
            </Controls>
        </Form>
    </Controls>
</MethodPresentation>
