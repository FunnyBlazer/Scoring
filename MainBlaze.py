from Application import *
from Predictors import *
import numpy as np
from tabulate import tabulate

if __name__ == "__main__":

    # GET INPUT DATA
    controller = Controller()
    builder = BuilderVectorBlaze()
    controller.builder = builder
    controller.buildVctForTestScoreCardBlaze()

    #print(builder.product.CreditBureau_df[['CREDITJOINT','CREDITOWNER','CREDITTYPE','CREDITDATE']])

    # GET OUTPUT DATA
    predictors_dwh  = TestScoreCardPredictors(builder.product.Application_df,builder.product.CreditBureau_df,builder.product.Behavioral_df)
    
    #print(dir(builder.product.Application_df))

    predictors_dwh.get_predictors_rez_df()

    # PRINT OUTPUT DATAFRAME
    print(tabulate(predictors_dwh.rez_df, headers='keys',tablefmt='psql',disable_numparse=True))
    #print(predictors_dwh.rez_df.head())