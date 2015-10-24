import datetime

def excel_date(date1):
    temp = dt.datetime(1899, 12, 31)
    delta = date1 - temp
    return float(delta.days) + (float(delta.seconds) / 86400)




if __name__ == "__main__":
    for x in range(100):
        print excel_date()
