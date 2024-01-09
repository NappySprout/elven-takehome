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
  new_txts = []
  #this is to remove duplicate transfer fees of the same txtHash
  gas_mem = set()
  for txt in txts:
    parsed_txt = {
      "type" : "TRANSFER_OUT" if txt["from"] == wallet_address.lower() else "TRANSFER_IN",
      "txHash" : txt["hash"],
      "datetime" : timestamp_to_zulu(int(txt["timeStamp"])).strftime('%Y-%m-%dT%H:%M:%SZ'),
      "contactIdentity" : [id for id in [txt["from"], txt["to"]] if id != wallet_address.lower()][0],
      "currency" : "KUB",
      "amount" : float(txt["value"])/(float(1e18))
    }
    gas_txt = {
      "type" : "TRANSFER_FEE",
      "txHash" : txt["hash"],
      "contactIdentity" : parsed_txt["contactIdentity"],
      "currency" : "KUB",
      "amount" : (float(txt["gasUsed"])*float(txt["gasPrice"])) /(float(1e18)) 
    }
    new_txts.append(parsed_txt)
    if txt["hash"] not in gas_mem:
      new_txts.append(gas_txt)
      gas_mem.add(txt["hash"])

  url = f"https://www.bkcscan.com/api?module=account&action=tokentx&address={wallet_address}"
  req = requests.get(url)
  tokentxts = req.json()["result"]
  tokentxts = [tokentxt for tokentxt in tokentxts if  start_timestamp <= int(tokentxt["timeStamp"]) <= end_timestamp]
  for tokentxt in tokentxts:
    parsed_txt = {
      "type" : "TRANSFER_OUT" if tokentxt["from"] == wallet_address.lower() else "TRANSFER_IN",
      "txHash" : tokentxt["hash"],
      "datetime" : timestamp_to_zulu(int(tokentxt["timeStamp"])).strftime('%Y-%m-%dT%H:%M:%SZ'),
      "contactIdentity" : [id for id in [tokentxt["from"], tokentxt["to"]] if id != wallet_address.lower()][0],
      "currency" : tokentxt["tokenSymbol"],
      "amount" : 1 if "value" not in tokentxt else float(tokentxt["value"]) / (1*(10**int(tokentxt["tokenDecimal"]))) #LPT tokens only have 1 amount
    }
    gas_txt = {
      "type" : "TRANSFER_FEE",
      "txHash" : tokentxt["hash"],
      "contactIdentity" : parsed_txt["contactIdentity"],
      "currency" : "KUB",
      "amount" : (float(tokentxt["gasUsed"])*float(tokentxt["gasPrice"])) /(float(1e18))  
    }
    
    new_txts.append(parsed_txt)
    if tokentxt["hash"] not in gas_mem: 
      new_txts.append(gas_txt)
      gas_mem.add(tokentxt["hash"])
  return new_txts
print(get_txtlist("0x5Cf6c83A471ECd030A67C6C1AFdD530bCD08e32D", "2021/05/30", "2021/05/31"))

