import os.path
import time
from datetime import date, datetime, timedelta

stops_dict = {
    "0": ('nonstop '),
    "1": ('1 stop '),
    "2": ('2 stops '),
    "3": ('nonstop ', '1 stop '),
    "4": ('1 stop ', '2 stops '),
    "5": ('nonstop ', '1 stop ', '2 stops '),
}

class openCsvAndRun:
    def __init__(self):
        self.date_set = set()

    def openCsvFile(self, file_csv):
        """
        :param file_csv: csv file name in the folder
        :return: split lists
        """
        directory = os.path.dirname(__file__)
        filename = os.path.join(directory, file_csv)
        testFile = open(filename).read()
        testFile.strip('\n')
        if file_csv == 'Destination List.csv':
            return testFile.split(',')
        else:
            split_by_n = testFile.split('\n')
            lst = [data_split.split('|') for data_split in split_by_n]
            return lst[:-1]

    def listsOfTrips(self):
        '''
        :return: creating list of data for each destiny [ date | price | destination | airline | direct ]
        '''
        csv_open_file = self.openCsvFile('Destination List.csv')
        destination_list_name = [destination.strip('\n') for destination in csv_open_file]
        data_list = [self.openCsvFile(f'{destination_list_name[trip]}.csv') for trip in range(len(csv_open_file) - 1)]
        return data_list[0]

    def splitToIndex(self):
        '''
        :return: list split by ", '"
        '''
        outside_list = []
        for outer_list in self.listsOfTrips():
            cleanDate = self.dateAndPlace(outer_list[0])
            middle_list = []
            for mid_list in outer_list[1:-1]:
                after_split = mid_list.split(',')
                clean_price = self.priceCleaner(after_split[0])
                clean_flight_details = self.flightDetials(after_split[1: 4])
                clean_stops = self.stopsClean(after_split[3: ])
                url = [cleanDate, outer_list[-1]]
                middle_list.append([clean_price, clean_flight_details, clean_stops, url])
            outside_list.append(middle_list)
        return outside_list

    def stopsClean(self, stops):
        stopA = stops[0].strip(" [''")
        stopB = stops[1].strip(" ']]")
        stops_list = []
        if stopA.startswith('nonstop') or stopA[2:6] == 'stop':
            if stopA[2: 6] == 'stop':
                stops_list.append(stopA[: 7])
            else:
                stops_list.append(stopA)
        if stopB.startswith('nonstop') or stopB[2:6] == 'stop':
            if stopB[2: 6] == 'stop':
                stops_list.append(stopB[: 7])
            else:
                stops_list.append(stopB)
        if len(stops_list) != 0:
            return stops_list
        else:
            return 'unknown', 'unknown'


    def flightDetials(self, flight_d):
        flight_A = flight_d[0].strip(" (''").replace('+1', '').replace('+2', '').split()
        flight_B = flight_d[1].strip(" ()''").replace('+1', '').replace('+2', '').split()
        flight_C = flight_d[2]
        flight_D = ''
        if flight_C[1] != '[':
            flight_D = flight_C.strip(" ()''").replace('+1', '').split()
        if flight_D == '':
            return flight_A, flight_B
        else:
            return flight_A, flight_B, flight_D


    def priceCleaner(self, price):
        try:
            return int(price.strip("[]''$"))
        except:
            pass


    def dateAndPlace(self, data):
        spliter = data.strip("[]").replace("'", '').split(',')
        return spliter[0], spliter[1][2:]

    def sortMainListByPrice(self):
        elmentList_a = self.splitToIndex()
        counter = 0
        sort_lst = []
        for elmentList in elmentList_a[1::2]:
            try:
                sortList = sorted(elmentList, key=lambda price: price[:])
                sort_lst.append(elmentList_a[counter])
                sort_lst.append(sortList)
                counter += 2
            except:
                pass

        return sort_lst

    def mostCeapestList(self):
        elmentList = self.sortMainListByPrice()
        sortList_a = sorted(elmentList, key=lambda price: price[:][0])
        return sortList_a

    def dateFrmat(self, dates):
        cln_date = dates.replace(' ', '').split('—')
        date_list = []
        for date_clean in cln_date:
            dates_a = time.strptime(date_clean, '%m/%d')
            dates_b = date(dates_a.tm_year, dates_a.tm_mon, dates_a.tm_mday)
            date_list.append(dates_b.strftime('%A, %d %B'))
        return date_list

    def printResults(self, results, stop=5, loops=3):
        counter = 0
        for pr_results in results():
            if len(pr_results[0][2]) != 2:
                stops = [pr_results[0][2][0], pr_results[0][2][0]]
            else:
                stops = pr_results[0][2]
            dates = self.dateFrmat(pr_results[1][3][0][1])
            if stops[0] in stops_dict[str(stop)] and stops[1] in stops_dict[str(stop)] and counter < loops:
                print(f"\nFlight: {pr_results[1][3][0][0]}\n"
                      f"Departure Flight : {dates[0]} --> {pr_results[0][1][0][0]} - {pr_results[0][1][0][1]} -->"
                      f"By : {' '.join(pr_results[0][1][0][2:])} --> {stops[0]} \n"
                      f"Return Flight : {dates[1]} --> {pr_results[0][1][1][0]} - {pr_results[0][1][1][1]} -->"
                      f"By : {' '.join(pr_results[0][1][1][2:])} --> {stops[1]}\n"
                      f"Price : ${pr_results[0][0]}\n"
                      f"{pr_results[1][3][1]}"
                      f"\n")
                counter += 1


###################################################################################################################

# stops_dict = {
#     "0": 'nonstop ',
#     "1": '1 stop ',
#     "2": '2 stops ',
#     "3": ('nonstop ', '1 stop '),
#     "4": ('1 stop', '2 stops'),
#     "5": ('nonstop ', '1 stop ', '2 stops '),
# }

run = openCsvAndRun()
run.printResults(run.mostCeapestList, stop=5, loops=5)


