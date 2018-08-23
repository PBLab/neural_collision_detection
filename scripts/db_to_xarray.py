import xarray as xr
import pandas as pd
import numpy as np

def load_db_into_ds(fname):
    """ Load a 'database' into a xarray.Dataset object """
    column_names = ['run_id', 'neuron', 'vasc', 'location', 'rotation', 'collisions']
    dtypes = {column_names[0]: 'category', column_names[1]: 'category', 
              column_names[2]: 'category', column_names[3]: str, column_names[4]: str,
              column_names[5]: str}
    df = pd.read_csv(fname, header=None, names=column_names, 
                     index_col=column_names[:3], dtype=dtypes)
    # Parse locations into three (x, y, z) columns
    locs = df.location\
        .str.split(' ', expand=True)\
        .rename(columns={0: 'x', 1: 'y', 2: 'z'})
    
    # Parse rotations into three (roll, yaw, pitch) columns
    rots = df.rotation\
        .str.split(' ', expand=True)\
        .rename(columns={0: 'r', 1: 'y', 2: 'p'})
    
    # Parse collision coordinates into a new DataFrame, x-y-z as columns and the neuron name
    # as a categorical index
    collisions = pd.DataFrame([], columns=['x', 'y', 'z'], index=[], dtype=np.float64)
    for idx, data in df.collisions.items():
        split = data.replace('|', ' ').split(' ')
        assert len(split) % 3 == 0  # x-y-z coords
        arr = np.array(split, dtype=np.float64).reshape((-1, 3))
        new_df = pd.DataFrame({'x': arr[:, 0], 'y': arr[:, 1], 'z': arr[:, 2],
                               column_names[0]: idx[0], column_names[1]: idx[1],
                               column_names[2]: idx[2]})
        for col_name in column_names[:3]:
           new_df[col_name] = new_df[col_name].astype('category')
        new_df = new_df.set_index(column_names[:3])
        collisions.append(new_df)
    
    ds = xr.Dataset({'location': locs, 'rotation': rots, 'collisions': collisions})
    return ds
    

if __name__ == '__main__':
    fname = r'X:\simulated_morph_data\results\agg_all_70_2.db'
    ds = load_db_into_ds(fname)
    print(df.head())
