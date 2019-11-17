from bs4 import BeautifulSoup as bs
from PyQt5.QtWebEngineWidgets import QWebEnginePage
from PyQt5 import QtCore, QtWidgets
import csv
import os.path
import sys
from time import sleep
from multiprocessing import Process
import time
from datetime import date, timedelta


class FormatDate:
    def __init__(self, original_date, long_stay, starting, destination, direct, loops, flexible, loops_to_run):
        if len(destination) == 0:
            self.destination = ['']
        else:
            self.destination = destination
        self.original_date = original_date
        self.time_to_stay = long_stay
        self.starting_point = starting
        self.direct = direct
        self.fix = flexible
        self.go_loop = loops_to_run
        if len(self.destination) >= len(self.starting_point):
            self.loops = loops - loops % len(self.destination)
        else:
            self.loops = loops - loops % len(self.starting_point)

    def mainFunction(self):
        '''
        :return: list of urls address [url1, url2 ...].
                 results of that function passing to Web_Loader class.
        '''

        urls_address = []
        self.counter = 0
        self.runLoop = 0
        self.loopTrip = self.countIndex(self.loops)
        for jump in range(self.loops):
            if jump % self.loopTrip[0] == 0 and jump != 0:
                self.runLoop = 0
                self.counter += 1

            elif self.loopTrip[1] == 0:
                self.runLoop = 0

            elif jump % self.loopTrip[1] == 0 and jump != 0 and self.fix == 'yes':
                self.runLoop += 1
            self.jump = jump
            urls_address.append(self.urlAddres())
        return urls_address

    def countIndex(self, totLoop):  #####
        if len(self.destination) < len(self.starting_point):
            alooPerDest = totLoop // len(self.starting_point)
            perLoop = self.alocaetionPerLoop(alooPerDest)
            return alooPerDest, perLoop
        else:
            alooPerDest = totLoop // len(self.destination)
            perLoop = self.alocaetionPerLoop(alooPerDest)
            return alooPerDest, perLoop

    def alocaetionPerLoop(self, alooPerDest):
        if self.go_loop == 0:
            return 0
        else:
            return alooPerDest // self.go_loop

    def dateAddDayDeparture(self, index):
        '''
        :return: changing the original departure date by one day in each loop [190301, 190302 ....]
        '''
        departure_date = time.strptime(str(self.original_date[index]), '%y%m%d')
        date_out = date(departure_date.tm_year, departure_date.tm_mon, departure_date.tm_mday) + \
                   timedelta(self.findRightDates())
        departure = (date_out.strftime('%Y-%m-%d'))
        return departure

    def findRightDates(self):

        func = {
            "a": self.jump - (self.loopTrip[0] * self.counter),
            "b": self.loopTrip[1],
        }

        if self.fix == 'no':
            return func["a"]

        elif self.fix == 'yes':
            return func["a"] % func["b"]

    def addDaysDeparture(self):
        '''
        :return: the results of dateAddDayDeparture function based on the sending condition.
        '''

        if len(self.original_date) == 1:
            return self.dateAddDayDeparture(0)
        else:
            return self.dateAddDayDeparture(self.counter)

    def dateAddDayArrivel(self, index):
        '''
        :return: adding days from departure date (dateAddDayDeparture) to return date based on self.time_to_stay.
        '''

        if self.fix == 'yes':
            self.runLoop = self.runLoop
        else:
            self.runLoop = 0
        if self.time_to_stay[index] != 0:
            departure = self.addDaysDeparture()
            date_return = time.strptime(departure, '%Y-%m-%d')
            date_return_i = date(date_return.tm_year, date_return.tm_mon,
                                 date_return.tm_mday) + timedelta(self.time_to_stay[index] + self.runLoop)
            arrivel = (date_return_i.strftime('%Y-%m-%d'))
            return arrivel
        else:
            return 0

    def addDaysArrivel(self):  ######
        '''
        :return: the results of dateAddDayArrivel function based on the sending condition.
        '''

        if len(self.time_to_stay) == 1 or \
                len(self.starting_point) >= 1 and len(self.destination) == 1 and len(self.time_to_stay) == 1:
            return self.dateAddDayArrivel(0)

        elif len(self.time_to_stay) > 1:
            return self.dateAddDayArrivel(self.counter)

    def startPoint(self):
        '''
        :return: the place of departure .
        '''

        if len(self.starting_point) == 1:
            return self.starting_point[0]
        else:
            return self.starting_point[self.counter]

    def urlAddres(self):
        '''
        :return: url address
        '''
        departure_date = self.addDaysDeparture()
        arriving_date = self.addDaysArrivel()
        start_point = self.startPoint()

        if len(self.destination) >= len(self.starting_point):
            self.url = f'https://www.kayak.com/flights/{start_point.upper()}-' \
                f'{self.destination[self.counter].upper()}/{departure_date}/{arriving_date}'

        elif len(self.destination) < len(self.starting_point):
            self.url = f'https://www.kayak.com/flights/{start_point.upper()}-' \
                f'{self.destination[0].upper()}/{departure_date}/{arriving_date}'

        # print(self.url)
        return self.url


class WebPage(QWebEnginePage):
    def __init__(self, num):
        super(QWebEnginePage, self).__init__()
        self.loadFinished.connect(self.handleLoadFinished)
        self.num = num
        self.location = set()

    def start(self, urls):
        self._urls = iter(urls)
        self.fetchNext()

    def fetchNext(self):
        try:
            url = next(self._urls)
            self.web_address = url
        except StopIteration:
            return False
        else:
            print(url)
            self.load(QtCore.QUrl(url))
        return True

    def processCurrentPage(self, html_str):
        self.html = html_str
        self.soup = bs(self.html, 'html.parser')
        blocks = self.soup.find_all('div', class_='inner-grid keel-grid')
        if len(blocks) != 0:
            all_results = []
            place_n_date = self.soup.title.text.split(',')
            all_results.append(place_n_date)
            for tag in blocks:
                results = []

                price = [cost.text for cost in tag.find_all('span', class_='price-text')[:1]]
                results.append(price)

                data = [details.text.replace('\n', '').replace('am', '').replace('pm', '')
                     for details in tag.find_all('div', class_='section times')]
                results.append((data[0].replace('–', ''), data[1].replace('–', '')))

                stops = [stop_q.text.replace('\n', '').replace('PFO ', '')
                         for stop_q in tag.find_all('div', class_='section stops')]
                results.append(stops)
                all_results.append(results)
            all_results.append(self.web_address)
            print('Well Done :-)')
            if self.num == 1:
                self.saveDataToCsv(all_results)
            else:
                self.saveDataToCsv(all_results)
                self.saveDestinationInFile(all_results[0][0])
        if not self.fetchNext():
            QtWidgets.qApp.quit()


    def handleLoadFinished(self):
        sleep(13)  # 17
        self.html = self.toHtml(self.processCurrentPage)


    def saveDataToCsv(self, data_list):
        directory = os.path.dirname(__file__)
        myFile = open(os.path.join(directory, f'{data_list[0][0]}.csv'), 'a', newline='')
        with myFile:
            writer = csv.writer(myFile, delimiter='|', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerows([data_list])
        myFile.close()

    def saveDestinationInFile(self, destinationList):
        directory = os.path.dirname(__file__)
        myFile = open(os.path.join(directory, 'Destination List.csv'), 'a', newline='')
        if destinationList in self.location:
            pass
        else:
            writer = csv.writer(myFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(''.join(f'{destinationList},').split(','))
            self.location.add(destinationList)
            myFile.close()



# **********************************************************************************************************************

starting = ['tlv']
destination = ['mil']

# **********************************************************************************************************************

original_date = [200501]
long_stay = [5]

# **********************************************************************************************************************

direct = 'false'

# **********************************************************************************************************************

flexible_date = 'no'  # ('yes' or 'no')
looping = 3

# **********************************************************************************************************************

searching = 20

# **********************************************************************************************************************

# **** START YOUR APPLICETION ****#

# **********************************************************************************************************************

url = FormatDate(original_date, long_stay, starting, destination,
                 direct, searching, flexible_date, looping).mainFunction()


####################################################################################

def func1():
    # sleep(3)
    app = QtWidgets.QApplication(sys.argv)
    webPage = WebPage(0)
    print('PART 1')
    webPage.start(url[:: 3])
    sys.exit(app.exec_())


def func2():
    sleep(5)  # 5
    app1 = QtWidgets.QApplication(sys.argv)
    webPage1 = WebPage(1)
    print('PART 2')
    webPage1.start(url[1:: 3])
    sys.exit(app1.exec_())


def func3():
    sleep(10)
    app2 = QtWidgets.QApplication(sys.argv)
    webPage2 = WebPage(1)
    print('PART 3')
    webPage2.start(url[2:: 3])
    sys.exit(app2.exec_())



if __name__ == '__main__':
    p1 = Process(name='p1', target=func1)
    p2 = Process(name='p2', target=func2)
    p3 = Process(name='p3', target=func3)
    p1.start()
    p2.start()
    p3.start()
