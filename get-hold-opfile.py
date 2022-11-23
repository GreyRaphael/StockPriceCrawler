import sys
import csv
from PriceCrawler import PriceProvider


def get_codelist(hold_file, volume):
    code_list = []
    with open(hold_file, "r", encoding="utf8") as file:
        reader = csv.DictReader(file)
        for record in reader:
            code = record["StockCode"]
            available_vol = eval(record["AvailableVolume"])
            if not available_vol > 0:
                continue
            vol = volume if (volume and volume < available_vol) else available_vol
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
    seperate_num = None

    if len(sys.argv) == 1:
        pass
    elif len(sys.argv) == 2:
        vol = int(sys.argv[1])
    elif len(sys.argv) == 3:
        vol = int(sys.argv[1])
        seperate_num = int(sys.argv[2])
    else:
        print("to many arguments")
        sys.exit(0)

    prefix_dir = "/home/gewei/i2swap/build/bin"
    stock_account = "2022101811"
    # code_list = get_codelist(f"{prefix_dir}/hold-2022101812.csv", vol) # double
    # code_list = get_codelist(f"{prefix_dir}/hold-2022101113.csv", vol) # mainSH
    code_list = get_codelist(f"{prefix_dir}/output/hold-{stock_account}.csv", vol)  # mainSZ

    print("begin crawler")
    obj = PriceProvider(code_list)
    price_list = obj.get_pricelist()
    price_list.sort(key=lambda x: x["f2"])
    print("end crawler")

    # write2csv
    output_list = obj.seperateList(price_list, N=seperate_num, writeFlag=False)
    print(f"output list length={len(output_list)}")
    obj.writeCSV(f"{prefix_dir}//StockPrice/opfile-{stock_account}.csv", output_list)
