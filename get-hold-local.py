import sys
import csv
from PriceCrawler import PriceProvider


def get_codelist(hold_file, volume):
    code_list = []
    with open(hold_file, "r", encoding="utf8") as file:
        reader = csv.DictReader(file)
        for record in reader:
            code = record["StockCode"]
            available_vol=eval(record["AvailableVolume"])
            if not available_vol>0: continue
            vol = volume if volume else available_vol
            if code.startswith("0") or code.startswith("3"):
                code_list.append(
                    {
                        "priceType": 1,
                        "direction": 2,
                        "volume": vol,
                        "SECUCODE": f"{code}.SZ",
                        'f2': eval(record["LastPrice"]),
                    }
                )
            elif code.startswith("6"):
                code_list.append(
                    {
                        "priceType": 1,
                        "direction": 2,
                        "volume": vol,
                        "SECUCODE": f"{code}.SH",
                        'f2': eval(record["LastPrice"]),
                    }
                )
    return code_list


if __name__ == "__main__":
    vol = None
    seperate_num=5

    if len(sys.argv) == 1:
        pass
    elif len(sys.argv) == 2:
        vol = int(sys.argv[1])
    elif len(sys.argv) == 3:
        vol = int(sys.argv[1])
        seperate_num=int(sys.argv[2])
    else:
        print("to many arguments")
        sys.exit(0)

    price_list = get_codelist("output/hold.csv", vol)

    # write2csv
    output_list = PriceProvider.seperateList(price_list, N=seperate_num, writeFlag=False)
    print(f"output list length={len(output_list)}")
    PriceProvider.writeCSV("output/opfile-hold.csv", output_list)
