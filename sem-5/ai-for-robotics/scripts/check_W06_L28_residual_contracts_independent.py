"""Independent source transcription, before L28 residual keyed access."""
import datetime, hashlib, json
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
data_pandas=pd.DataFrame({'Name':['John','Anna','Peter','Linda'],'Location':['New York','Paris','Berlin','London'],'Age':[24,13,53,33]})
assert data_pandas.iloc[1,2] == 13
assert data_pandas.iloc[1,1] == 'Paris'
assert data_pandas.iloc[2,2] == 53
try:eval('Data_pandas.iloc[1,2]')
except NameError:pass
else:raise AssertionError('Undefined uppercase identifier must raise NameError')
result={'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'phase':'Before current or historical L28 keyed materials','pandasVersion':pd.__version__,'assertionCount':4,'results':{'iloc[1,2]':13,'iloc[1,1]':'Paris','iloc[2,2]':53,'undefinedUppercase':'NameError'},'scriptSha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
(ROOT/'audits/W06-L28-residual-contracts-independent-checks.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
