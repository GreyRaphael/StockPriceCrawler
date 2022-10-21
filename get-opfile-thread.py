import sys
from PriceCrawler import PriceProvider

def get_codelist(stock_file, direction, volume):
    code_list = []
    with open(stock_file, "r", encoding="utf8") as file:
        for line in file:
            code = line.rstrip("\n")
            if code.startswith("0") or code.startswith("3"):
                code_list.append(
                    {
                        "priceType": 1,
                        "direction": direction,
                        "volume": volume,
                        "SECUCODE": f"{code}.SZ",
                    }
                )
            elif code.startswith("6"):
                code_list.append(
                    {
                        "priceType": 1,
                        "direction": direction,
                        "volume": volume,
                        "SECUCODE": f"{code}.SH",
                    }
                )
    return code_list


if __name__ == "__main__":
    stockfile = "input/stocks.txt"
    direction = 1
    volume = 100
    seperate_num = None

    if len(sys.argv) == 1:
        pass
    elif len(sys.argv) == 2:
        stockfile = sys.argv[1]
    elif len(sys.argv) == 3:
        stockfile = sys.argv[1]
        direction = int(sys.argv[2])
    elif len(sys.argv) == 4:
        stockfile = sys.argv[1]
        direction = int(sys.argv[2])
        volume = int(sys.argv[3])
    elif len(sys.argv) == 5:
        stockfile = sys.argv[1]
        direction = int(sys.argv[2])
        volume = int(sys.argv[3])
        seperate_num = int(sys.argv[4])
    else:
        print("to many arguments")
        sys.exit(0)

    code_list = get_codelist(stockfile, direction, volume)
    print("begin crawler")
    obj=PriceProvider(code_list)
    price_list= obj.get_pricelist()
    price_list.sort(key=lambda x: x['f2'])
    print("end crawler")

    
    # write2csv
    output_list = obj.seperateList(price_list, N=seperate_num, writeFlag=False)
    print(f"output list length={len(output_list)}")
    obj.writeCSV("output/opfile.csv", output_list)
