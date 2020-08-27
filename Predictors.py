from functools import reduce

import numpy as np
import pandas as pd
from pandas.tests.scalar import timestamp
from tabulate import tabulate

#from Config import predictors_fun

class Predictors():
    #construct object
    def __init__(self,app_df,cb_df,beh_df,predictors_list_df,predictor_cash_df):

        self.app_df = app_df
        self.cb_df = cb_df
        self.beh_df = beh_df 
        self.rez_df = None
        self.predictors_list_df = predictors_list_df
        self.predictors_cash_df = predictor_cash_df

        self.predictors_fun={
        'MAX_DATE_OPEN_CARD': self.max_date_open_card,
        'MIN_DATE_OPEN_CARD':self.min_date_open_card,
        'CNT_CLOSED_CASH_POS':self.cnt_closed_cash_pos,
        'AGE_YEARS_REAL':self.age_years_real,
        'EDUCATION':self.education,
        'ALL_CASH_POS':self.all_cash_pos,
        'CB_MAXAGRMNTHS_1_3':self.cb_maxagrmnths_1_3,
        'CB_MAXAGRMNTHS_2_3':self.cb_maxagrmnths_2_3,
        'CB_MAXAGRMNTHS_3_3':self.cb_maxagrmnths_3_3
        }
        # print(self.predictors_fun)
    def add_unknown_columns(self,df,features):


        
        for key,value in features.items():
            if key not in df:

                if value=='d':
                    df[key]= np.datetime64('NaT')
                elif value =='c':
                    df[key] = str(np.nan)
                else:
                    df[key] = np.nan
        pass

    def is_card(self,credit_type):
        return 1 if credit_type == 4  else 0

    def age_years_real(self):

        self.add_unknown_columns(self.app_df,{'SYSDATE':'d','BIRTH':'d'})

        v_df = self.app_df[['SK_APPLICATION']].assign(AGE_YEARS_REAL=(self.app_df['SYSDATE'] - self.app_df['BIRTH'])/np.timedelta64(1,'Y'))

        return v_df

    def education(self):

        # check attributes
        self.add_unknown_columns(self.app_df,{'EDUCATION':'c'})
        self.add_unknown_columns(self.beh_df,{'EDUCATION':'c'})

        df = reduce(
        lambda  left,right: pd.merge(left,right,how='outer',on=['SK_APPLICATION']),
        [self.app_df,self.beh_df.rename(columns={"EDUCATION": "BEHEDUCATION"})]
        )
        v_df= self.app_df[['SK_APPLICATION']].assign(EDUCATION=(df['EDUCATION'].fillna(df['BEHEDUCATION'])))

        return v_df
    
    def max_date_open_card(self):

        # check attributes
        self.add_unknown_columns(self.cb_df,{'CREDITJOINT':'n','CREDITOWNER':'c','CREDITTYPE':'n','CREDITDATE':'d'})

        v_df=self.cb_df[
        (self.cb_df['CREDITJOINT'] == 1) &
        (self.cb_df['CREDITOWNER'] == '0') &
        (self.cb_df['CREDITTYPE'].apply(lambda x:1 if x in {4,14,24} else 0)) == 1
        ].groupby(['SK_APPLICATION']).agg({'CREDITDATE':np.max}).rename(columns={"CREDITDATE": "MAX_DATE_OPEN_CARD"})
    
       # df.rename(columns={"B": "c"})

        return v_df
    
    def min_date_open_card(self):

        self.add_unknown_columns(self.cb_df,{'CREDITJOINT':'n','CREDITOWNER':'c','CREDITTYPE':'n','CREDITDATE':'d'})

        v_df = self.cb_df[
        (self.cb_df['CREDITJOINT'] == 1) &
        (self.cb_df['CREDITOWNER'] == '0') &
        (self.cb_df['CREDITTYPE'].apply(lambda x:1 if x in {4,14,24} else 0)) == 1
        ].groupby(['SK_APPLICATION']).agg({'CREDITDATE':np.min}).rename(columns={"CREDITDATE": "MIN_DATE_OPEN_CARD"})
  

        return v_df

    def all_cash_pos(self):

        self.add_unknown_columns(self.cb_df,{'CREDITJOINT':'n','CREDITOWNER':'c','CREDITTYPE':'n','CREDITDATE':'d'})

        v_df = self.cb_df[
        (self.cb_df['CREDITJOINT'] == 1) &
        (self.cb_df['CREDITOWNER'] == '0') &
        (self.cb_df['CREDITTYPE'].apply(lambda x:1 if x in {5,8,13} else 0)) == 1
        ].groupby(['SK_APPLICATION']).agg({'SK_APPLICATION':np.count_nonzero}).rename(columns={"SK_APPLICATION": "ALL_CASH_POS"})

        return v_df

    def cnt_closed_cash_pos(self):

        self.add_unknown_columns(self.cb_df,{'CREDITJOINT':'n','CREDITOWNER':'c','CREDITTYPE':'n','CREDITDATE':'d'})

        v_df = self.cb_df[
        (self.cb_df['CREDITJOINT'] == 1) &
        (self.cb_df['CREDITOWNER'] == '0') &
        (self.cb_df['CREDITTYPE'].apply(lambda x:1 if x in {4,14,24} else 0)) == 1
        #(df['SK_DATE_DECISION']==df['SK_DATE_DECISION'])
        ].groupby(['SK_APPLICATION']).agg({'SK_APPLICATION':np.count_nonzero}).rename(columns={"SK_APPLICATION": "CNT_CLOSED_CASH_POS"})

        #print(v_df)

        return v_df

    def cb_maxagrmnths_1_3(self):

        self.add_unknown_columns(self.cb_df,{'CREDITJOINT':'n','CREDITOWNER':'c','CREDITSUMDEBT':'n','CREDITSUM':'n',
                                            'CREDITENDDATEFACT':'d','CREDITENDDATE':'d','CREDITSUMOVERDUE':'n','CREDITDATE':'d'}
        )
        self.add_unknown_columns(self.app_df,{'SYSDATE':'d'})

        v_df_pre = reduce(
        lambda  left,right: pd.merge(left,right,how='outer',on=['SK_APPLICATION']), 
        [
        #APPLICATIONS
        pd.DataFrame({"SK_APPLICATION":self.app_df['SK_APPLICATION'].unique()}),
        #NUMACTIVECONCB 
        self.cb_df[
        ((self.cb_df['CREDITOWNER'] == '0') | (self.cb_df['CREDITOWNER'].isna())) &
        ((self.cb_df['CREDITSUMDEBT'].isna()) & (self.cb_df['CREDITSUM']>40000)) &
        (self.cb_df['CREDITJOINT'] == 1) &
        (self.cb_df['CREDITENDDATE'].isna()) &
        (
            (self.cb_df['CREDITENDDATE'].isna()) | 
            (
                ((self.cb_df['CREDITSUMOVERDUE']>200) & (self.cb_df['CREDITENDDATE'] > self.app_df.iloc[0]['SYSDATE'])) |
                ((self.cb_df['CREDITENDDATE'] < self.app_df.iloc[0]['SYSDATE']))
            )
        )
        ].groupby(['SK_APPLICATION']).agg({'SK_APPLICATION':np.count_nonzero}).rename(columns={"SK_APPLICATION": "NUMACTIVECONCB"}).reset_index(),
        #MINMONTHLASTAPP
        self.cb_df[
        ((self.cb_df['CREDITOWNER'] == '0') | (self.cb_df['CREDITOWNER'].isna())) &
        ((self.cb_df['CREDITSUMDEBT'].isna()) & (self.cb_df['CREDITSUM']>40000)) &
        (self.cb_df['CREDITJOINT'] == 1) &
        (self.cb_df['CREDITJOINT'].notna()) &
        (
            (self.cb_df['CREDITENDDATE'].isna()) | 
            (
                ((self.cb_df['CREDITSUMOVERDUE']>200) & (self.cb_df['CREDITENDDATE'] > self.app_df.iloc[0]['SYSDATE'])) |
                (self.cb_df['CREDITENDDATE'] < self.app_df.iloc[0]['SYSDATE'])
            )
        )

        ].assign(MONTHLASTAPP = (self.app_df.iloc[0]['SYSDATE']-self.cb_df['CREDITDATE'])/np.timedelta64(1,'M')
        ).groupby(['SK_APPLICATION']).agg({'MONTHLASTAPP':np.min}).rename(columns={"MONTHLASTAPP": "MINMONTHLASTAPP"}).reset_index()
        ]
        )

        v_df_pre['CB_MAXAGRMNTHS_1_3'] = np.where(
        (v_df_pre['NUMACTIVECONCB']==1) & 
        (v_df_pre['MINMONTHLASTAPP']<3),
        1,
        0
        )
         
        v_df = v_df_pre[['SK_APPLICATION','CB_MAXAGRMNTHS_1_3']]
            
            # .groupby(['SK_APPLICATION']
            # ).agg({'SK_APPLICATION':np.count_nonzero}
            # ).rename(columns={"SK_APPLICATION": "CB_MAXAGRMNTHS_1_3"}).reset_index()

        return v_df


    def cb_maxagrmnths_2_3(self):

        self.add_unknown_columns(self.cb_df,{'CREDITJOINT':'n','CREDITOWNER':'c','CREDITSUMDEBT':'n','CREDITSUM':'n',
                                            'CREDITENDDATEFACT':'d','CREDITENDDATE':'d','CREDITSUMOVERDUE':'n','CREDITDATE':'d'}
        )

        self.add_unknown_columns(self.app_df,{'SYSDATE':'d'})

        v_df_pre = reduce(
        lambda  left,right: pd.merge(left,right,how='outer',on=['SK_APPLICATION']), 
        [
        #APPLICATIONS
        pd.DataFrame({"SK_APPLICATION":self.app_df['SK_APPLICATION'].unique()}),
        #NUMACTIVECONCB 
        self.cb_df[
        ((self.cb_df['CREDITOWNER'] == '0') | (self.cb_df['CREDITOWNER'].isna())) &
        ((self.cb_df['CREDITSUMDEBT'].isna()) & (self.cb_df['CREDITSUM']>40000)) &
        (self.cb_df['CREDITJOINT'] == 1) &
        (self.cb_df['CREDITENDDATEFACT'].isna()) &
        (
            (self.cb_df['CREDITENDDATE'].isna()) | 
            (
                ((self.cb_df['CREDITSUMOVERDUE']>200) & (self.cb_df['CREDITENDDATE'] > self.app_df.iloc[0]['SYSDATE'])) |
                ((self.cb_df['CREDITENDDATE'] < self.app_df.iloc[0]['SYSDATE']))
            )
        )
        ].groupby(['SK_APPLICATION']).agg({'SK_APPLICATION':np.count_nonzero}).rename(columns={"SK_APPLICATION": "NUMACTIVECONCB"}).reset_index(),
        #MINMONTHLASTAPP
        self.cb_df[
        ((self.cb_df['CREDITOWNER'] == '0') | (self.cb_df['CREDITOWNER'].isna())) &
        ((self.cb_df['CREDITSUMDEBT'].isna()) & (self.cb_df['CREDITSUM']>40000)) &
        (self.cb_df['CREDITJOINT'] == 1) &
        (self.cb_df['CREDITENDDATEFACT'].isna()) &
        (
            (self.cb_df['CREDITENDDATE'].isna()) | 
            (
                ((self.cb_df['CREDITSUMOVERDUE']>200) & (self.cb_df['CREDITENDDATE'] > self.app_df.iloc[0]['SYSDATE'])) |
                (self.cb_df['CREDITENDDATE'] < self.app_df.iloc[0]['SYSDATE'])
            )
        )

        ].assign(MONTHLASTAPP = (self.app_df.iloc[0]['SYSDATE']-self.cb_df['CREDITDATE'])/np.timedelta64(1,'M')
        ).groupby(['SK_APPLICATION']).agg({'MONTHLASTAPP':np.min}).rename(columns={"MONTHLASTAPP": "MINMONTHLASTAPP"}).reset_index()
        ]
        )

        v_df_pre['CB_MAXAGRMNTHS_2_3'] = np.where(
        (v_df_pre['NUMACTIVECONCB']==2) & 
        (v_df_pre['MINMONTHLASTAPP']<3),
        1,
        0
        )
         
        v_df = v_df_pre[['SK_APPLICATION','CB_MAXAGRMNTHS_2_3']]
            
            # .groupby(['SK_APPLICATION']
            # ).agg({'SK_APPLICATION':np.count_nonzero}
            # ).rename(columns={"SK_APPLICATION": "CB_MAXAGRMNTHS_1_3"}).reset_index()

        return v_df

    def cb_maxagrmnths_3_3(self):

        self.add_unknown_columns(self.cb_df,{'CREDITJOINT':'n','CREDITOWNER':'c','CREDITSUMDEBT':'n','CREDITSUM':'n',
                                            'CREDITENDDATEFACT':'d','CREDITENDDATE':'d','CREDITSUMOVERDUE':'n','CREDITDATE':'d'}
        )

        self.add_unknown_columns(self.app_df,{'SYSDATE':'d'})

        v_df_pre = reduce(
        lambda  left,right: pd.merge(left,right,how='outer',on=['SK_APPLICATION']), 
        [
        #APPLICATIONS
        pd.DataFrame({"SK_APPLICATION":self.app_df['SK_APPLICATION'].unique()}),
        #NUMACTIVECONCB 
        self.cb_df[
        ((self.cb_df['CREDITOWNER'] == '0') | (self.cb_df['CREDITOWNER'].isna())) &
        ((self.cb_df['CREDITSUMDEBT'].isna()) & (self.cb_df['CREDITSUM']>40000)) &
        (self.cb_df['CREDITJOINT'] == 1) &
        (self.cb_df['CREDITENDDATEFACT'].isna()) &
        (
            (self.cb_df['CREDITENDDATE'].isna()) | 
            (
                ((self.cb_df['CREDITSUMOVERDUE']>200) & (self.cb_df['CREDITENDDATE'] > self.app_df.iloc[0]['SYSDATE'])) |
                ((self.cb_df['CREDITENDDATE'] < self.app_df.iloc[0]['SYSDATE']))
            )
        )
        ].groupby(['SK_APPLICATION']).agg({'SK_APPLICATION':np.count_nonzero}).rename(columns={"SK_APPLICATION": "NUMACTIVECONCB"}).reset_index(),
        #MINMONTHLASTAPP
        self.cb_df[
        ((self.cb_df['CREDITOWNER'] == '0') | (self.cb_df['CREDITOWNER'].isna())) &
        ((self.cb_df['CREDITSUMDEBT'].isna()) & (self.cb_df['CREDITSUM']>40000)) &
        (self.cb_df['CREDITJOINT'] == 1) &
        (self.cb_df['CREDITENDDATEFACT'].isna()) &
        (
            (self.cb_df['CREDITENDDATE'].isna()) | 
            (
                ((self.cb_df['CREDITSUMOVERDUE']>200) & (self.cb_df['CREDITENDDATE'] > self.app_df.iloc[0]['SYSDATE'])) |
                (self.cb_df['CREDITENDDATE'] < self.app_df.iloc[0]['SYSDATE'])
            )
        )

        ].assign(MONTHLASTAPP = (self.app_df.iloc[0]['SYSDATE']-self.cb_df['CREDITDATE'])/np.timedelta64(1,'M')
        ).groupby(['SK_APPLICATION']).agg({'MONTHLASTAPP':np.min}).rename(columns={"MONTHLASTAPP": "MINMONTHLASTAPP"}).reset_index()
        ]
        )

        v_df_pre['CB_MAXAGRMNTHS_3_3'] = np.where(
        (v_df_pre['NUMACTIVECONCB']==3) & 
        (v_df_pre['MINMONTHLASTAPP']<3),
        1,
        0
        )
         
        v_df = v_df_pre[['SK_APPLICATION','CB_MAXAGRMNTHS_3_3']]
            
            # .groupby(['SK_APPLICATION']
            # ).agg({'SK_APPLICATION':np.count_nonzero}
            # ).rename(columns={"SK_APPLICATION": "CB_MAXAGRMNTHS_1_3"}).reset_index()

        return v_df


    def get_predictors_dwh_df(self)->None:

        df_base = pd.DataFrame({"SK_APPLICATION":self.app_df['SK_APPLICATION'].unique()})

        dfs = [
        df_base,
        self.cnt_closed_cash_pos(),                 # cnt_closed_cash_pos
        self.max_date_open_card(),                  # max_date_open_card
        self.min_date_open_card(),                  # min_date_open_card
        self.all_cash_pos(),                        # all_cash_pos
        self.age_years_real(),                      # age_years_real
        self.education(),                           # education
        self.cb_maxagrmnths_2_3()                   # cb_maxagrmnths_2_3
        ]

        df_merged = reduce(lambda  left,right: pd.merge(left,right,how='outer',on=['SK_APPLICATION']), dfs)

        self.rez_df = df_merged

    def get_predictors_blaze_df(self)->None:

        df_base = pd.DataFrame({"SK_APPLICATION":self.app_df['SK_APPLICATION'].unique()})

        dfs=[df_base]
        #print(dfs)

        for index,row in self.predictors_list_df.iterrows():
            #print(row['NAME'])
            v_dfs=self.get_predictor_value(row['NAME'])

            #print(v_dfs)

            dfs.append(v_dfs)
    
        df_merged = reduce(lambda  left,right: pd.merge(left,right,how='outer',on=['SK_APPLICATION']), dfs)

        self.rez_df = df_merged



    def get_predictor_value(self,p_name):

        if not self.predictors_cash_df.empty:

            for index,row in self.predictors_cash_df.iterrows():
                
                if row['NAME'] == p_name and row['CLASS'] == 'scoreCardPredictor':
                    
                    v_df = pd.DataFrame({
                        'SK_APPLICATION':[self.predictors_cash_df.loc[index,'SK_APPLICATION']],
                        row['NAME']:[self.predictors_cash_df.loc[index,'VALUE']]
                    })
                    return v_df
        else:
                
                #print(row['NAME'])
                v_df = self.predictors_fun[p_name]()
        return v_df

