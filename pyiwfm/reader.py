from collections import namedtuple
import pandas as pd
import os
import re

def read_elements(file):
    with open(file, 'r') as fh:
        line = fh.readline()
        while line.find('IE') < 0 and line.find('IDE(1)') < 0:
            line = fh.readline()
        fh.readline()
        dfe = pd.read_csv(fh, sep='\s+',
                          header=None, names=['1', '2', '3', '4', '5'],
                          index_col=0, comment='C')
    if len(dfe.columns) == 4:
        dfe.columns = ['1', '2', '3', '4']
    return dfe


def read_nodes(file):
    with open(file, 'r') as fh:
        line = fh.readline()
        while line.find('/ND') < 0:
            line = fh.readline()
        fh.readline()
        return pd.read_csv(fh, sep='\s+',
                           header=None, names=['x', 'y'],
                           index_col=0, comment='C')


def read_nodes(file):
    with open(file, 'r') as fh:
        line = fh.readline()
        while line.find('/ND') < 0:
            line = fh.readline()
        fh.readline()
        return pd.read_csv(fh, sep='\s+',
                           header=None, names=['x', 'y'],
                           index_col=0, comment='C')


def read_hydrograph(file):
    with open(file, 'r') as fh:
        line = fh.readline()
        while line.find('/ NOUTH') < 0:
            line = fh.readline()
        nrows=int(re.findall('\d+',line)[0])
        line=fh.readline() # skip next line before continuing
        line=fh.readline()
        while line.startswith('C'):
            pos=fh.tell()
            line=fh.readline()
        fh.seek(pos)
        return pd.read_csv(fh, sep='\s+',
                           header=None,
                           names=['iouthl', 'x', 'y', 'iouth', 'sep', 'Calibration_ID'], 
                           nrows=nrows)


def read_stratigraphy(file):
    with open(file, 'r') as fh:
        line = fh.readline()
        while (line.find('/NL') < 0):
            line = fh.readline()
        fields = line.split()
        nlayers = int(str.strip(fields[0]))  # number of layers in the file
        layer_cols = []
        for i in range(1, nlayers+1):
            layer_cols.append('A%d' % i)
            layer_cols.append('L%d' % i)
        #
        while (line.find('ID') < 0 and line.find('GSE') < 0) or \
                (line.find('ID') < 0 and line.find('ELV') < 0):
            line = fh.readline()
        fh.readline()
        cols = ['NodeID', 'GSE']+layer_cols
        return pd.read_csv(fh, sep='\s+', comment='C', index_col=0,
                           header=None, names=cols, usecols=cols)


def get_index(df0):
    # split the first column into date and time
    date_col = df0.iloc[:, 0].str.split('_', expand=True).iloc[:, 0]
    # set index to date part
    idx = pd.to_datetime(date_col)
    idx.index = idx.index
    idx.name = 'Time'
    idx.freq = pd.infer_freq(idx)
    return idx


def rearrange(df0, drop_first=False):
    if drop_first:
        # drop the first columnn as it is index now
        df0 = df0.drop(0, axis=1)
    df0.columns = df0.columns.astype('str')
    df0 = df0.dropna(axis=1)
    return df0.astype('float')


def read_gwhead(gwheadfile, nlayers):
    dfh = pd.read_fwf(gwheadfile, skiprows=5, sep='\s+', nrows=1)
    colspecs = [(i*12+22, i*12+34) for i in range(0, len(dfh.columns))]
    colspecs = [(0, 22)]+colspecs
    df = pd.read_fwf(gwheadfile, skiprows=6, header=None, sep='\s+', colspecs=colspecs)
    # 4 layers --> 4 dataframes, one for each layer
    layer_df = {i: df.iloc[i::nlayers] for i in range(nlayers)}
    # get index from first layer as a time index
    idx = get_index(layer_df[0])
    # rearrange and drop columns
    layer_df[0] = rearrange(layer_df[0], drop_first=True)  # ,cols_shift_left=1)
    for i in range(1, nlayers):
        layer_df[i] = rearrange(layer_df[i], drop_first=True)  # ,cols_shift_left=2)
    # set index of each dataframe to time index
    for i in range(nlayers):
        layer_df[i].index = idx[0:len(layer_df[i])]
    return layer_df

# caching for gwhead


def gwh_feather_filename(file, layer=0):
    return f'{file}.{layer}.ftr'


def cache_gwh_feather(file, dfgh):
    for k in dfgh.keys():
        ffile = f'{file}.{k}.ftr'
        dfx = dfgh[k].reset_index().to_feather(ffile)


def load_gwh_feather(file, nlayers):
    dfgh = {}
    for k in range(nlayers):
        ffile = f'{file}.{k}.ftr'
        df = pd.read_feather(ffile)
        dfgh[k] = df.set_index(df.columns[0])
    return dfgh


def read_and_cache(gwh_file, nlayers, recache=False):
    if recache or not os.path.exists(gwh_feather_filename(gwh_file)):
        dfgwh = read_gwhead(gwh_file, nlayers)
        cache_gwh_feather(gwh_file, dfgwh)
    else:
        dfgwh = load_gwh_feather(gwh_file, nlayers)
    return dfgwh


#
GridData = namedtuple('GridData', ['elements', 'nodes', 'stratigraphy', 'nlayers'])


def load_data(elements_file, nodes_file, stratigraphy_file):
    el = read_elements(elements_file)
    nodes = read_nodes(nodes_file)
    strat = read_stratigraphy(stratigraphy_file)
    # FIXME: not a great way to get layers but works. need a cleaner implementation
    nlayers = len(strat.columns)//2
    return GridData(el, nodes, strat, nlayers)


def load_gwh(gwh_file, nlayers, recache=False):
    gwh = read_and_cache(gwh_file, nlayers, recache)
    return gwh
