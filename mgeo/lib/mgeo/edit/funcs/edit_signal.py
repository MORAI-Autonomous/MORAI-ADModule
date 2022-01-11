import ast
import numpy as np

def delete_signal(signal_set, signal):
    """signal_set에서 signal을 제거한다"""
    if signal_set is None:
        raise BaseException('None is passed for an argument signal_set')
    
    if signal is None:
        raise BaseException('None is passed for an argument signal')
            
    signal_set.remove_signal(signal)


def update_signal(signal_set, link_set, signal, field_name, old_val, new_val):    
    if field_name == 'idx':
        if new_val in signal_set:
            raise BaseException('The signal (id = {}) already exists in the signal list.'.format(new_val))

        setattr(signal, field_name, new_val)
        signal_set.pop(old_val)
        signal_set[new_val] = signal

    elif field_name == 'dynamic':
        dynamic = ast.literal_eval(new_val)
        setattr(signal, field_name, dynamic)

    elif field_name == 'point':
        point_array = np.array(new_val)
        setattr(signal, field_name, point_array)

    else:
        setattr(signal, field_name, new_val)


def string_to_list(TL_set):
    for i in TL_set:
        if type(TL_set[i].link_id_list) != list:
            setattr(TL_set[i], 'link_id_list', ast.literal_eval(TL_set[i].link_id_list))