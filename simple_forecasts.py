import pandas as pd
import numpy as np
from statistics import mean


def create_errors(df, actual, forecast):
    '''Append an error series and an error percentage series to the
       dataframe.'''
    df[forecast + ' Error'] = df[forecast] - df[actual]
    df[forecast + ' Error %'] = (df[forecast] - df[actual]) / df[actual]
    return df


def naive(df, label):
    '''Append a naive forecast, error, and error percentage series
       to the dataframe.'''
    df['Naive'] = df[label].shift(1, axis=0)
    create_errors(df, label, 'Naive')
    return df


def average(df, label):
    '''Append a average forecast, error, and error percentage series
       to the dataframe.'''
    temp = []
    for row in range(len(df)):
        if row == 0:
            temp.append(np.nan)
        else:
            temp.append(mean(df[label].loc[:row]))
    df['Average'] = temp
    create_errors(df, label, 'Average')
    return df


def moving_avg(df, label, lag):
    '''Append a moving average forecast, error, and error percentage
       series to the dataframe.'''
    temp = []
    for row in range(len(df)):
        if row < lag:
            temp.append(np.nan)
        else:
            temp.append(mean(df[label].loc[row-lag:row]))
    df['Moving Average ' + '(' + str(lag) + ')'] = temp
    create_errors(df, label, 'Moving Average ' + '(' + str(lag) + ')')
    return df


def exp_smooth(df, label, alpha):
    '''Append an exponential smoothing forecast, error, and error 
       percentage series to the dataframe.'''
    temp = []
    for row in range(len(df)):
        value = 0
        if row == 0:
            temp.append(np.nan)
        else:
            for r in range(row-1, -1, -1):
                value += df[label].loc[r] * alpha * (1-alpha)**(r)
            temp.append(value)
    df['Exp Smooth ' + str(alpha)] = temp
    create_errors(df, label, 'Exp Smooth ' + str(alpha))
    return df


def compare_errors(df, non_errors):
    '''Create a dataframe comparing the errors different modeling
       techniques, generated by the function create_errors.'''
    models = [col for col in df.columns if 'Error' not in col][non_errors:]
    model_errors = [col for col in df.columns if 'Error' in col and '%' not in col]
    model_error_pers = [col for col in df.columns if 'Error %' in col]

    errors = pd.DataFrame([], index=models, columns=['MAD', 'RMSE', 'MAPE'])

    errors['MAD'] = [df[me].abs().mean() for me in model_errors]
    errors['RMSE'] = [(df[me]**2).mean()**(1/2) for me in model_errors]
    errors['MAPE'] = [df[mep].abs().mean() for mep in model_error_pers]

    return errors


if __name__ == '__main__':
    # Set up
    df = pd.read_excel('overhead_costs.xlsx', sheet_name='Data')
    original_cols = len(df.columns)
    label = 'Overhead'

    # Creating the forecast series
    df = naive(df, label)
    df = average(df, label)
    for alpha in [0.8, 0.6, 0.4, 0.2]:
        df = exp_smooth(df, label, alpha)
    for lag in [2, 3, 4, 5]:
        df = moving_avg(df, label, lag)


    # Create the errors dataframe and compare the models
    errors = compare_errors(df, original_cols)
    errors.sort_values(by='MAPE', inplace=True)

    # Export to Excel
    # errors.to_excel('smooth_ohcosts_e.xlsx', sheet_name='Errors')
    # df.to_excel('smooth_ohcosts.xlsx', sheet_name='Models')

    print(errors)
