from pyiwfm import reader

def test_svsim_head():
    file='data/svsim_beta/Results/SVSim_GW_HeadAll.out'
    nlayers=9
    dfheads = reader.read_gwhead(file, nlayers=nlayers)
    assert len(dfheads.keys()) == nlayers
    df1 = dfheads[0]
    assert len(df1) == 505

def test_read_and_cache_svsim_head():
    file='data/svsim_beta/Results/SVSim_GW_HeadAll.out'
    nlayers=9
    dfheads = reader.read_and_cache(file, nlayers=nlayers, recache=False)
    assert len(dfheads.keys()) == nlayers
    df1 = dfheads[0]
    assert len(df1) == 505
