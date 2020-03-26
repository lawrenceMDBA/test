"""
Simple tools to work with RTC data inputs / outputs with pandas. This functionality works at least from Python 3.6 onwards.
"""
from pathlib import Path
import pandas as pd
import rtctools.data.pi as pi
import rtctools.data.rtc as rtc

def drop_qualifiers(df):
    if df.columns.get_level_values('qualifier_id').unique().size==1:
        df.columns = df.columns.droplevel(level='qualifier_id')
    return df

def PIXML_2_DF(fname, rtcDataConfig='default', multi_index_cols=False, squeezeQualifiers=True):
    """
    Return the data of a PI-XML as a pandas DataFrame with Timeseries index
    """
    f = Path(fname)
    # Read data
    if rtcDataConfig == 'default':
        rtcDataConfig = f.parents[1].joinpath('input/rtcDataConfig.xml')
        if not rtcDataConfig.exists():
            print("NO rtcDataConfig.xml was found at default location")
    else:
        try:
            rtcDataConfig = Path(rtcDataConfig)
        except:
            rtcDataConfig = None
            print("NO rtcDataConfig.xml was found at provided path")
        
    dataconfig = rtc.DataConfig(rtcDataConfig.parent)
    ts = pi.Timeseries(dataconfig, f.parent, f.stem, binary=False)
    
    # Make it a DataFrame
    df = pd.DataFrame.from_dict(dict(ts.items()))
    df.index = ts.times
    df.index.name = "time"

    if multi_index_cols:
        # If you want PI/FEWS location id, etc. as multi-level column names, execute
        # lines below:
        col_tuples = [dataconfig.pi_variable_ids(x) for x in df.columns]
        # QualifierId is list, which is not hashable. Make tuple instead.
        col_tuples = [(a, b, tuple(c)) for a, b, c in col_tuples]
        df.columns = pd.MultiIndex.from_tuples(col_tuples, names=['location_id', 'parameter_id', 'qualifier_id'])
#        df.index.name
    
        if squeezeQualifiers: # Loose qualifiers when they are all the same
            df = drop_qualifiers(df)
    
    return df


def RTC_PIXML_IO_2_DF(case, rtcDataConfig='default', multi_index_cols=False, squeezeQualifiers=True):
    input_file = Path(case).joinpath(r"input/timeseries_import.xml")
    output_file = Path(case).joinpath(r"output/timeseries_export.xml")
    df_in = PIXML_2_DF(input_file, rtcDataConfig=rtcDataConfig, multi_index_cols=multi_index_cols, 
                       squeezeQualifiers=False)
    df_out = PIXML_2_DF(output_file, rtcDataConfig=rtcDataConfig, multi_index_cols=multi_index_cols, 
                       squeezeQualifiers=False)
    # df = df_in.join(df_out)
    df = df_in.copy()
    df[df_out.columns] = df_out
    
    if squeezeQualifiers:
        df = drop_qualifiers(df)
    return df

def main():
    print("XML 2 CSV")
    case = Path.cwd()
    input_file = Path(case).joinpath(r"input/timeseries_import.xml")
    output_file = Path(case).joinpath(r"input/timeseries_import.csv")
    df = PIXML_2_DF(input_file, rtcDataConfig='default', multi_index_cols=False, squeezeQualifiers=True)
    df.to_csv(output_file, sep = ';')
    print("XML 2 CSV: converted timeseries_import")
    input_file = Path(case).joinpath(r"output/timeseries_export.xml")
    output_file = Path(case).joinpath(r"output/timeseries_export.csv")
    df = PIXML_2_DF(input_file, rtcDataConfig='default', multi_index_cols=False, squeezeQualifiers=True)
    df.to_csv(output_file, sep = ';')
    print("XML 2 CSV: converted timeseries_export")

if __name__ == "__main__": main()

# Test assuming this file is in some subfolder of the case folder:
if False:
    case = Path.cwd().parents[0]
    df = RTC_PIXML_IO_2_DF(case, rtcDataConfig='default', multi_index_cols=True, squeezeQualifiers=True)
    fname = case.joinpath(r"output/timeseries_export.xml")
    df = PIXML_2_DF(fname, rtcDataConfig='default', multi_index_cols=False, squeezeQualifiers=True)
    
