import requests
from dateutil.parser import parse
from dateutil import tz
from datetime import datetime, timezone

def local_to_epoch(local_date: str) -> int:
  #replace naive datetime to localtime
  local_datetime = parse(local_date).replace(tzinfo=tz.tzlocal())
  #timestamp method takes into account tzinfo,  will convert to correct epoch time
  return int(local_datetime.timestamp())

def timestamp_to_zulu(timestamp: int) -> datetime:
  #convert timestamp to zulu time
  return datetime.fromtimestamp(timestamp, tz=timezone.utc)

def get_txtlist(wallet_address, local_start_date, local_end_date):
  start_timestamp = local_to_epoch(local_start_date)
  end_timestamp = local_to_epoch(local_end_date)

  url = f"https://www.bkcscan.com/api?module=account&action=txlist&address={wallet_address}&starttimestamp={start_timestamp}&endtimestamp={end_timestamp}"
  req = requests.get(url)
  txts = req.json()["result"]
  impt_keys = ["from", "to", "hash", "timeStamp", "value", "gasUsed", "gasPrice"]
  new_txts = []
  for txt in txts:
    new_txt = {k:v for (k,v) in txt.items() if k in impt_keys}
    parsed_txt = {
      "type" : "TRANSFER_OUT" if new_txt["from"] == wallet_address.lower() else "TRANSFER_IN",
      "txHash" : new_txt["hash"],
      "datetime" : timestamp_to_zulu(int(new_txt["timeStamp"])).strftime('%Y-%m-%dT%H:%M:%SZ'),
      "contactIdentity" : [id for id in [new_txt["from"], new_txt["to"]] if id != wallet_address.lower()][0],
      "currency" : "KUB",
      "amount" : float(new_txt["value"])/(float(1e18))
    }
    gas_txt = {
      "type" : "TRANSFER_FEE",
      "txHash" : new_txt["hash"],
      "contactIdentity" : parsed_txt["contactIdentity"],
      "currency" : "KUB",
      "amount" : (float(new_txt["gasUsed"])*float(new_txt["gasPrice"])) /(float(1e18)) 
    }
    new_txts.append(parsed_txt)
    new_txts.append(gas_txt)
  print(new_txts[1])

print(local_to_epoch("2023/01/09"))
print(timestamp_to_zulu(local_to_epoch("2023/01/09")))

print("____")
def timestamp_to_local(timestamp: int) -> datetime:
  #convert timestamp to zulu time
  return datetime.fromtimestamp(timestamp)
print(timestamp_to_local(1622316593))
print(timestamp_to_local(1622395266))
get_txtlist("0x5Cf6c83A471ECd030A67C6C1AFdD530bCD08e32D", "2021/05/30", "2021/05/31")

