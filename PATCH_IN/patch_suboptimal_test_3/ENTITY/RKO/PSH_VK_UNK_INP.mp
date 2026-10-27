<?xml version="1.0" encoding="UTF-8"?>
<MethodPresentation classId="RKO" formatVersion="1.2" shortName="PSH_VK_UNK_INP">
    <Properties>
        <Hotkey>Alt+V</Hotkey>
        <UserDriven>true</UserDriven>
    </Properties>
    <Parameters/>
    <Variables/>
    <Controls>
        <Form>
            <Properties>
                <Caption>[ПСБ] Ввести кол-во операций во постановке, переоформлению и снятию с учета УНК</Caption>
                <Height>248</Height>
                <ValidateName>Form1</ValidateName>
                <Width>434</Width>
            </Properties>
            <Controls>
                <Label>
                    <Properties>
                        <Caption>Дата операций</Caption>
                        <Height>24</Height>
                        <Left>8</Left>
                        <Qualifier>%PARAM%.P_DATE</Qualifier>
                        <Tips>Поясняющая надпись (Дата операций)</Tips>
                        <Top>8</Top>
                        <ValidateName>Label1</ValidateName>
                        <Width>132</Width>
                    </Properties>
                </Label>
                <Date>
                    <Properties>
                        <Caption>Дата операций</Caption>
                        <CheckValidate>true</CheckValidate>
                        <ClassId>DATE</ClassId>
                        <EnabledInner>false</EnabledInner>
                        <Left>148</Left>
                        <Qualifier>%PARAM%.P_DATE</Qualifier>
                        <TabIndex>2</TabIndex>
                        <Tips>Дата операций</Tips>
                        <Top>8</Top>
                        <ValidateName>Date1</ValidateName>
                    </Properties>
                </Date>
                <Button>
                    <Properties>
                        <Caption>OK</Caption>
                        <Height>24</Height>
                        <Left>68</Left>
                        <Qualifier>OK</Qualifier>
                        <TabIndex>3</TabIndex>
                        <Tips>Выполнить операцию</Tips>
                        <Top>208</Top>
                        <ValidateName>Ok</ValidateName>
                        <Width>140</Width>
                    </Properties>
                </Button>
                <Button>
                    <Properties>
                        <Caption>Отмена</Caption>
                        <Height>24</Height>
                        <Left>216</Left>
                        <Qualifier>CANCEL</Qualifier>
                        <TabIndex>4</TabIndex>
                        <Tips>Отказ от выполнения</Tips>
                        <Top>208</Top>
                        <ValidateName>Cancel</ValidateName>
                        <Width>140</Width>
                    </Properties>
                </Button>
                <Label>
                    <Properties>
                        <Caption>Кол-во операций по постановке УНК на учет</Caption>
                        <Height>24</Height>
                        <Left>8</Left>
                        <Qualifier>%PARAM%.P_SET</Qualifier>
                        <Tips>Поясняющая надпись (Кол-во операций по постановке УНК на учет)</Tips>
                        <Top>40</Top>
                        <ValidateName>Label2</ValidateName>
                        <Width>376</Width>
                    </Properties>
                </Label>
                <Number>
                    <Properties>
                        <Caption>Кол-во операций по постановке УНК на учет</Caption>
                        <ClassId>NUMBER</ClassId>
                        <Height>24</Height>
                        <Left>388</Left>
                        <Qualifier>%PARAM%.P_SET</Qualifier>
                        <TabIndex>0</TabIndex>
                        <Tips>Кол-во операций по постановке УНК на учет</Tips>
                        <Top>40</Top>
                        <ValidateName>Number1</ValidateName>
                        <Width>28</Width>
                    </Properties>
                </Number>
                <Label>
                    <Properties>
                        <Caption>Кол-во операций по переоформлению УНК</Caption>
                        <Height>24</Height>
                        <Left>8</Left>
                        <Qualifier>%PARAM%.P_CH</Qualifier>
                        <Tips>Поясняющая надпись (Кол-во операций по переоформлению УНК)</Tips>
                        <Top>104</Top>
                        <ValidateName>Label3</ValidateName>
                        <Width>376</Width>
                    </Properties>
                </Label>
                <Number>
                    <Properties>
                        <Caption>Кол-во операций по переоформлению УНК</Caption>
                        <ClassId>NUMBER</ClassId>
                        <Height>24</Height>
                        <Left>388</Left>
                        <Qualifier>%PARAM%.P_CH</Qualifier>
                        <TabIndex>0</TabIndex>
                        <Tips>Кол-во операций по переоформлению УНК</Tips>
                        <Top>104</Top>
                        <ValidateName>Number2</ValidateName>
                        <Width>28</Width>
                    </Properties>
                </Number>
                <Label>
                    <Properties>
                        <Caption>Кол-во операций по снятию с учета УНК/кредитного договора</Caption>
                        <Height>24</Height>
                        <Left>8</Left>
                        <Qualifier>%PARAM%.P_REM</Qualifier>
                        <Tips>Поясняющая надпись (Кол-во операций по снятию с учета УНК)</Tips>
                        <Top>168</Top>
                        <ValidateName>Label4</ValidateName>
                        <Width>376</Width>
                    </Properties>
                </Label>
                <Number>
                    <Properties>
                        <Caption>Кол-во операций по снятию с учета УНК</Caption>
                        <ClassId>NUMBER</ClassId>
                        <Height>24</Height>
                        <Left>388</Left>
                        <Qualifier>%PARAM%.P_REM</Qualifier>
                        <TabIndex>0</TabIndex>
                        <Tips>Кол-во операций по снятию с учета УНК</Tips>
                        <Top>168</Top>
                        <ValidateName>Number3</ValidateName>
                        <Width>28</Width>
                    </Properties>
                </Number>
                <Label>
                    <Properties>
                        <Caption>Кол-во операций по постановке кредитного договора на учет</Caption>
                        <Height>24</Height>
                        <Left>8</Left>
                        <Qualifier>%PARAM%.P_SET_CR</Qualifier>
                        <Tips>Поясняющая надпись (Кол-во операций по постановке кредитного договора на учет)</Tips>
                        <Top>72</Top>
                        <ValidateName>Label5</ValidateName>
                        <Width>376</Width>
                    </Properties>
                </Label>
                <Number>
                    <Properties>
                        <Caption>Кол-во операций по постановке кредитного договора на учет</Caption>
                        <ClassId>NUMBER</ClassId>
                        <Height>24</Height>
                        <Left>388</Left>
                        <Qualifier>%PARAM%.P_SET_CR</Qualifier>
                        <TabIndex>0</TabIndex>
                        <Tips>Кол-во операций по постановке кредитного договора на учет</Tips>
                        <Top>72</Top>
                        <ValidateName>Number4</ValidateName>
                        <Width>28</Width>
                    </Properties>
                </Number>
                <Label>
                    <Properties>
                        <Caption>Кол-во операций по переоформлению кредитного договора</Caption>
                        <Height>24</Height>
                        <Left>8</Left>
                        <Qualifier>%PARAM%.P_CH_CR</Qualifier>
                        <Tips>Поясняющая надпись (Кол-во операций по переоформлению кредитного договора)</Tips>
                        <Top>136</Top>
                        <ValidateName>Label6</ValidateName>
                        <Width>376</Width>
                    </Properties>
                </Label>
                <Number>
                    <Properties>
                        <Caption>Кол-во операций по переоформлению кредитного договора</Caption>
                        <ClassId>NUMBER</ClassId>
                        <Height>24</Height>
                        <Left>388</Left>
                        <Qualifier>%PARAM%.P_CH_CR</Qualifier>
                        <TabIndex>0</TabIndex>
                        <Tips>Кол-во операций по переоформлению кредитного договора</Tips>
                        <Top>136</Top>
                        <ValidateName>Number5</ValidateName>
                        <Width>28</Width>
                    </Properties>
                </Number>
            </Controls>
        </Form>
    </Controls>
</MethodPresentation>
