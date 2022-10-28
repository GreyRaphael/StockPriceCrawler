import csv
from PriceCrawler import PriceProvider


def get_codelist(filename_list):
    hold_volume_list = [99, 99, 109, 109, 109, 202]
    sell_volume_list = [98, 99, 9, 101, 109, 202]
    record_lists = []
    for filename in filename_list:
        with open(f"output/{filename}", "r", encoding="utf8") as file:
            reader = csv.DictReader(file)
            record_list = [record for record in reader]
        record_lists.append(record_list)

    dict_list = []
    for tup in zip(*record_lists, sell_volume_list, hold_volume_list):
        for record in tup[:4]:
            dict_list.append(
                {
                    "priceType": 1,
                    "direction": 2,
                    "volume": tup[4],
                    "hold": tup[5],
                    "SECUCODE": record["SECUCODE"],
                    "f2": record["f2"],
                }
            )
    return dict_list


if __name__ == "__main__":
    filename_list = ["sz00.csv", "sz30.csv", "sh60.csv", "sh688.csv"]
    code_list = get_codelist(filename_list)
    print(f"code list length={len(code_list)}")
    obj = PriceProvider(code_list)
    obj.writeCSV(f"output/suigu.csv", code_list)
