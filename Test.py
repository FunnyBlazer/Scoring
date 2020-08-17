# from dateutil import parser
# import re
# import pandas as pd
# #from Parse import *

# v_time =parser.parse('03.10.2012 00:00:00', dayfirst=True)
# #print(v_time.month)

# #print(v_time)

# # data=c|ApprovalCharacteristics[48].variation|1
# # n|ApprovalCharacteristics[49].integerValue|0

# # regex = re.compile(r'(.*?)\|ApprovalCharacteristics\[(\d+)\]\.(.*)\|(.*?)\s*$')

# # for line in data.split('\n'):    

# #     print(re.findall(regex,line)[0])



# # v_dict = parse_vct_str(test_str,df_dict,rx_dict)
# # print(v_dict['APPROVALCHARACTERISTIC'])
# # df = get_df_txt('APPROVALCHARACTERISTIC',v_dict)


# d = {'option1': ['1', '0', '1', '1'], 'option2': ['0', '0', '1', '0'], 'option3': ['1', '1', '0', '0']}
# df = pd.DataFrame(d)
# print(df)

# for index,row in df.iterrows():
#     #print (row['option1'])
#     if index == 1:
#         df1 = {'1':[df.loc[index,'option1']],'2':[df.loc[index,'option2']]}
#         print (row['option1'])

# print(pd.DataFrame(df1))

# from pycallgraph import PyCallGraph
# from pycallgraph.output import GraphvizOutput
# from Main import load_data_frame_blaze_str,test_str

# with PyCallGraph(output=GraphvizOutput()):
#     load_data_frame_blaze_str(test_str)



# from sklearn.externals import joblib

# saved_pipeline = joblib.load(filename='model_top_up.pkl')

import xgboost as xgb
import pandas as pd 


# data={'avg_dpd0':[2.3006134969325154],
#     'cnt_good_pos':[0],
#     'cnt_uniq_phones':[None],
#     'days_appr_first_not_rev':[5624],
#     'cnt_unsuccessful_weeks_24m':[3],
#     'instalment_count_paid_intime':[83],
#     'avg_dpd0_36m':[5.28333333333333],
#     'cnt_inst_to_pay_not_rd':[0],
#     'product_combination_last':[0.0201207243460765],
#     'cnt_part_ep':[None],
#     'avg_dpd0_12m':[14.2],
#     'flag_paid_off_after_dpd':[3],
#     'cnt_rej_9m':[4],
#     'days_last_full_ep':[4091]}

# data={'CURRENT_CARD_UTILIZED_NEW_XGB': [0.13633333333333333],
#         'CNT_AVG_DAYS_BETWEEN_APPL_24M': [0.0], 
#         'SUM_AMT_CREDIT': [556603.5], 
#         'CNT_APPLICATIONS': [12.0], 
#         'MAX_DPD_6': [0.0], 
#         'SCO_CASH_XSELL': [0.9927988063153145], 
#         'MONTHS_ID_PUBLISH': [204.0], 
#         'MAX_LTH_WO_PD_36': [36], 
#         'CNT_INST_12M': [0], 'AGE': [67.0], 
#         'AMT_MAX_ANNUITY': [24136.98], 
#         'MONTHS_TILL_FREEDOM': [94.0], 
#         'CBMAXDPD12': [0.0], 
#         'AVG_DAYS_BETWEEN_APPS': [82.0], 
#         'DD_CHANGE_MOBIL': [2684.0], 
#         'CNT_DAY_LAST_CREDIT': [869.0], 
#         'MAX_AMT_CREDIT_CUR': [105000.0], 
#         'AMT_PAYMENTS_TOTAL': [175852.16], 
#         'CNT_MAX_MONTHS_TILL_PLANCLOSED': [-43.12903225806452], 
#         'AMT_LIMIT_CREDIT_CARD': [None], 
#         'CNT_MAX_DAYS_OVERDUE': [15], 
#         'ALL_CASH_POS': [9], 
#         'RECEIVABLE_TO_CREDIT_CUR': [0.136], 
#         'ANNUITY_TO_CREDIT_CUR': [0.0], 
#         'CNT_CONTRACT_CASH_ACTIVE': [0.0], 
#         'CNT_DPD_0PL_EV_T_AL': [0.008], 
#         'CRED_LENGTH':[3152.0]
#     }


# data={
#         'CURRENT_CARD_UTILIZED_NEW_XGB': [None],
#         'CNT_AVG_DAYS_BETWEEN_APPL_24M': [None], 
#         'SUM_AMT_CREDIT': [None], 
#         'CNT_APPLICATIONS': [None], 
#         'MAX_DPD_6': [None], 
#         'SCO_CASH_XSELL': [None], 
#         'MONTHS_ID_PUBLISH': [32.0], 
#         'MAX_LTH_WO_PD_36': [None], 
#         'CNT_INST_12M': [None], 
#         'AGE': [22.0], 
#         'AMT_MAX_ANNUITY': [None], 
#         'MONTHS_TILL_FREEDOM': [None], 
#         'CBMAXDPD12': [None], 
#         'AVG_DAYS_BETWEEN_APPS': [None], 
#         'DD_CHANGE_MOBIL': [None], 
#         'CNT_DAY_LAST_CREDIT': [None], 
#         'MAX_AMT_CREDIT_CUR': [None], 
#         'AMT_PAYMENTS_TOTAL': [None], 
#         'CNT_MAX_MONTHS_TILL_PLANCLOSED': [None], 
#         'AMT_LIMIT_CREDIT_CARD': [None], 
#         'CNT_MAX_DAYS_OVERDUE': [None], 
#         'ALL_CASH_POS': [None], 
#         'RECEIVABLE_TO_CREDIT_CUR': [None], 
#         'ANNUITY_TO_CREDIT_CUR': [None], 
#         'CNT_CONTRACT_CASH_ACTIVE': [0.0], 
#         'CNT_DPD_0PL_EV_T_AL': [None], 
#         'CRED_LENGTH':[None]
#     }


#f= pd.DataFrame(data)


df = pd.read_csv("scoring_PTB_1.csv",sep=';')
xgtest = xgb.DMatrix(df.values)

#print(df)

bst = xgb.Booster({'nthread': 4})  # init model
bst.load_model('pos_ptb_model_for_blaze')  # load data

pred = bst.predict(xgtest)
pd.DataFrame(1-pred).to_csv('out.csv',index=False,float_format='%.15f')
#print(pd.DataFrame(pred).to_excel('out.xlsx'))
#print(list(map(lambda x: 1-x, pred)))

# pred = bst.predict(xgb.DMatrix(df))
# print(pred)
# print(list(map(lambda x: 1 - x, pred)))
