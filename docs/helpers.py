import pandas as pd

def getFrequencyTable(df, column):
    return pd.concat([df[column].value_counts(), df[column].value_counts(normalize=True).round(2)], axis=1)

def describe_complete(df, skipna=False):
    stats = {}
    stats["count"] = df.count()
    stats["unique"] = 0
    stats["mean"] = df.mean(skipna=skipna)
    stats["min"] = df.min(skipna=skipna)
    stats["quant_25"] = df.quantile(0.25)
    stats["quant_50"] = df.quantile(0.5)
    stats["quant_75"] = df.quantile(0.75)
    stats["max"] = df.max(skipna=skipna)
    stats["mode"] = ""
    stats["var"] = df.var(numeric_only=True, skipna= skipna)
    stats["std"] = df.std(skipna= skipna)
    stats["skew"] = df.skew(numeric_only=True, skipna= skipna)
    stats["kurt"] = df.kurt(numeric_only=True, skipna= skipna)

    stats_df = pd.DataFrame(stats)
    for column in df.columns:
        stats_df.loc[stats_df.index == column, "mode"] = "|".join([str(x) for x in df[column].mode()])
        stats_df.loc[stats_df.index == column, "unique"] = df.value_counts(column).count()

    return stats_df