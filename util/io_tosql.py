
import pandas as pd
import sys
import re


def sql_cols(df, usage="sql"):
    cols = tuple(df.columns)
    if usage == "sql":
        cols_str = str(cols).replace("'", "`")
        if len(df.columns) == 1:
            cols_str = cols_str[:-2] + ")"  # to process dataframe with only one column
        return cols_str
    elif usage == "format":
        base = "'%%(%s)s'" % cols[0]
        for col in cols[1:]:
            base += ", '%%(%s)s'" % col
        return base
    elif usage == "values":
        base = "%s=VALUES(%s)" % (cols[0], cols[0])
        for col in cols[1:]:
            base += ", `%s`=VALUES(`%s`)" % (col, col)
        return base


def to_sql(tb_name, conn, dataframe, type="update", chunksize=2000):
    """
    Dummy of pandas.to_sql, support "REPLACE INTO ..." and "INSERT ... ON DUPLICATE KEY UPDATE (keys) VALUES (values)"
    SQL statement.

    Args:
        tb_name: str
            Table to insert get_data;
        conn:
            DBAPI Instance
        dataframe: pandas.DataFrame
            Dataframe instance
        type: str, optional {"update", "replace", "ignore"}, default "update"
            Specified the way to update get_data. If "update", then `conn` will execute "INSERT ... ON DUPLICATE UPDATE ..."
            SQL statement, else if "replace" chosen, then "REPLACE ..." SQL statement will be executed; else if "ignore" chosen,
            then "INSERT IGNORE ..." will be excuted;
        chunksize: int
            Size of records to be inserted each time;
        **kwargs:

    Returns:
        None
    """

    df = dataframe.copy()
    df = df.fillna("None")
    df = df.applymap(lambda x: re.sub('([\'\"\\\])', '\\\\\g<1>', str(x)))
    cols_str = sql_cols(df)
    for i in range(0, len(df), chunksize):
        # print("chunk-{no}, size-{size}".format(no=str(i/chunksize), size=chunksize))
        df_tmp = df[i: i + chunksize]
        if type == "replace":
            sql_base = "REPLACE INTO `{tb_name}` {cols}".format(
                tb_name=tb_name,
                cols=cols_str
            )
            sql_val = sql_cols(df_tmp, "format")
            vals = tuple([sql_val % x for x in df_tmp.to_dict("records")])
            sql_vals = "VALUES ({x})".format(x=vals[0])
            for i in range(1, len(vals)):
                sql_vals += ", ({x})".format(x=vals[i])
            sql_vals = sql_vals.replace("'None'", "NULL")

            sql_main = sql_base + sql_vals

        elif type == "update":
            sql_base = "INSERT INTO `{tb_name}` {cols}".format(
                tb_name=tb_name,
                cols=cols_str
            )
            sql_val = sql_cols(df_tmp, "format")
            vals = tuple([sql_val % x for x in df_tmp.to_dict("records")])
            sql_vals = "VALUES ({x})".format(x=vals[0])
            for i in range(1, len(vals)):
                sql_vals += ", ({x})".format(x=vals[i])
            sql_vals = sql_vals.replace("'None'", "NULL")

            sql_update = "ON DUPLICATE KEY UPDATE {0}".format(
                sql_cols(df_tmp, "values")
            )

            sql_main = sql_base + sql_vals + sql_update

        elif type == "ignore":
            sql_base = "INSERT IGNORE INTO `{tb_name}` {cols}".format(
                tb_name=tb_name,
                cols=cols_str
            )
            sql_val = sql_cols(df_tmp, "format")
            vals = tuple([sql_val % x for x in df_tmp.to_dict("records")])
            sql_vals = "VALUES ({x})".format(x=vals[0])
            for i in range(1, len(vals)):
                sql_vals += ", ({x})".format(x=vals[i])
            sql_vals = sql_vals.replace("'None'", "NULL")

            sql_main = sql_base + sql_vals

        if sys.version_info.major == 2:
            sql_main = sql_main.replace("u`", "`")
        sql_main = sql_main.replace("%", "%%")
        conn.execute(sql_main)
