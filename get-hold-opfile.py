import sys
import csv
from PriceCrawler import PriceProvider


def get_codelist(hold_file, volume):
    code_list = []
    with open(hold_file, "r", encoding="utf8") as file:
        reader = csv.DictReader(file)
        for record in reader:
            code = record["StockCode"]
            vol = volume if volume else record["AvailableVolume"]
            if code.startswith("0") or code.startswith("3"):
                code_list.append(
                    {
                        "priceType": 1,
                        "direction": 2,
                        "volume": vol,
                        "SECUCODE": f"{code}.SZ",
                    }
                )
            elif code.startswith("6"):
                code_list.append(
                    {
                        "priceType": 1,
                        "direction": 2,
                        "volume": vol,
                        "SECUCODE": f"{code}.SH",
                    }
                )
    return code_list


if __name__ == "__main__":
    vol = None

    if len(sys.argv) == 1:
        pass
    elif len(sys.argv) == 2:
        vol = int(sys.argv[1])
    else:
        print("to many arguments")
        sys.exit(0)

    code_list = get_codelist("/home/gewei/i2swap/build/bin/output/hold.csv", vol)
    print("begin crawler")
    obj = PriceProvider(code_list)
    price_list = obj.get_pricelist()
    price_list.sort(key=lambda x: x["f2"])
    print("end crawler")

    # write2csv
    output_list = obj.seperateList(price_list, writeFlag=False)
    print(f"output list length={len(output_list)}")
    obj.writeCSV("output/opfile.csv", output_list)
