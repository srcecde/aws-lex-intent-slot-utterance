import os
role = os.environ["ROLE"] if "ROLE" in os.environ else ""
bucket_name = os.environ["BUCKET"] if "BUCKET" in os.environ else ""
bucket_key = os.environ["KEY"]if "KEY" in os.environ else ""
lex_func_name = os.environ["LEX"]if "LEX" in os.environ else ""
trigger_bucket = os.environ["TRIGGER"]if "TRIGGER" in os.environ else ""
