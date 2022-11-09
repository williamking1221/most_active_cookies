import argparse
import csv
import sys


class CookieProcessor():
    def __init__(self):
        """
        Initialize a dictionary of key:date --> value:dictionary of {cookies: number of occurrences}
        """
        self.date_to_cookie_dict = {}

    def process_cookies_csv(self, path):
        """
        Process the csv file and update the dictionary for key: date --> value: cookie --> count
        :param path: path to the csv file
        :return: void
        """
        with open(path, newline='') as cookies_log:
            reader = csv.DictReader(cookies_log)
            for row in reader:
                cookie = row['cookie']
                date = row['timestamp'].split("T")[0]       # Timestamp is a string of a Date and a T and a time
                if date not in self.date_to_cookie_dict:
                    self.date_to_cookie_dict[date] = {cookie: 1}
                else:
                    if cookie not in self.date_to_cookie_dict[date]:
                        self.date_to_cookie_dict[date][cookie] = 1
                    else:
                        self.date_to_cookie_dict[date][cookie] += 1

    def find_active_cookies(self, date):
        """
        Goes through the date_to_cookies_dict to find the date required, and access the value.
        Create a dummy variable that holds the highest number of occurrences
        Among the values (key: cookie --> value: number of occurrences), if value >= dummy variable above, append to
        a set, update the dummy variable, clear the set, and add the cookie to the empty set.
        :param date: target date
        :return: set of most active cookies for the target date
        """
        most_active_cookies = set()
        max_occurrences = 0
        if date in self.date_to_cookie_dict:
            for cookie in self.date_to_cookie_dict[date]:
                if self.date_to_cookie_dict[date][cookie] > max_occurrences:
                    max_occurrences = self.date_to_cookie_dict[date][cookie]
                    most_active_cookies.clear()
                    most_active_cookies.add(cookie)
                elif self.date_to_cookie_dict[date][cookie] == max_occurrences:
                    most_active_cookies.add(cookie)
            for cookie in most_active_cookies:
                print(cookie)

            return most_active_cookies
        # No cookies in that date. We are not told what to do in this case, but we print "No Cookies"
        else:
            print('No Cookies on this date')
            return 'No Cookies on this date'


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(
        prog='most_active_cookie.py',
        description='Program that calculates most active cookies on a date from a CSV file and prints them out',
    )
    arg_parser.add_argument("path")
    arg_parser.add_argument("--date", "-d")
    args = arg_parser.parse_args(sys.argv[1:])
    if args.date is None:
        print("Please add -d followed by a date")
    # Process the arguments
    cookie_processor = CookieProcessor()
    cookie_processor.process_cookies_csv(args.path)
    cookie_processor.find_active_cookies(args.date)
