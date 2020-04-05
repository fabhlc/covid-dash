from numpy import nan
import re

def group_age(input_column):
    ''' If input age is an integer, it groups it correctly. Otherwise, fixes string.'''
    output_column = []

    def rangeify(z):
        # Takes in integer and outputs range
        flr = int(round(z - 4.5, -1))
        clg = flr + 9
        return f'{flr}-{clg}'

    for y in input_column:
        try:
            if type(y) == int:
                if y < 20:
                    output_column.append('<20')
                else:
                    output_column.append(rangeify(y))
            elif '>' in y:
                # e.g. ">70"
                num = int(re.findall("[0-9]+", y)[0])
                output_column.append(rangeify(num))
            elif (y not in order_dict.keys()) or ('<' in y):
                # e.g. '10-19' or '<10'
                try:
                    first_num = int(re.findall('[0-9]+', y)[0])
                    if first_num < 20:
                        output_column.append('<20')
                    else:
                        output_column.append(y) # may need fixing
                except:
                    output_column.append(y)
                    pass
            else:
                output_column.append(y)
        except:
            output_column.append('')
    return output_column

order_dict = {
        '<20': 1,
        '20-29': 2,
        '30-39': 3,
        '40-49': 4,
        '50-59': 5,
        '60-69': 6,
        '70-79': 7,
        '80-89': 8,
        '90-99': 9,
        '100-109': 10,
        'Not Reported': 11,
        '': 12
    }
inv_dict = {v: k for k, v in order_dict.items()}

def order_agegroups(input_column):
    ''' Input age column and output an ordered one'''
    output_column = []
    for i in input_column:
        try:
            output_column.append(order_dict[i])
        except:
            output_column.append(nan)

    return output_column

def inverse_order_dict(input_val):
    return inv_dict[input_val]
