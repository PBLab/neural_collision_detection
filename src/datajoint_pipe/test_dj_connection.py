import datajoint as dj

from dj_tables import SCHEMA_NAME

schema = dj.schema(SCHEMA_NAME, locals())