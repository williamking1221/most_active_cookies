import string
import unittest
import csv
import datetime
import random
import math

from most_active_cookie import CookieProcessor


class ProducingData:

    def gen_test_data(self, num_unique_cookies=20, num_total_cookies=100, num_dates=10, num_shuffles=10,
                      max_chars=16, all_cookies_same_len=True, multiple_max=False, exists=True):
        """
        Generates the test data set and a solution. Builds the test data set out into a csv.
        :param num_unique_cookies: Number of unique cookies
        :param num_total_cookies: Total number of cookies
        :param num_dates: Number of dates
        :param num_shuffles: Number of shuffles, more shuffles mean more flat distribution of number of cookies
        :param max_chars: Number of max characters of the cookies
        :param all_cookies_same_len: Do all cookie names have the same length?
        :param multiple_max: Are there multiple cookies with max_occurrences in the query date
        :param exists: Does the date queried exist?
        :return: query date and solution (for testing), and makes a list of list to be converted to a csv
        """
        cookie_list = self.gen_cookies(num_unique_cookies, max_chars, all_cookies_same_len)
        date_list = [self.gen_random_timestamp() for k in range(num_dates)]
        counts = self.gen_counts(num_unique_cookies, num_total_cookies, num_shuffles)
        dates_dict, query_idx, solution_set = self.gen_dates(counts, num_dates, multiple_max)

        solution = set(cookie_list[i] for i in solution_set)
        if exists:
            query_date = date_list[query_idx]
        else:
            query_date = self.gen_random_timestamp()
            while query_date in date_list:
                query_date = self.gen_random_timestamp()
            solution = "No Cookies on this date"

        test_data = []
        for i in range(num_dates):
            for k in dates_dict[i]:
                row = list()
                row.append([cookie_list[k], date_list[i]])
                test_data.extend(row)
        self.convert_to_csv(test_data)

        return query_date.split("T")[0], solution

    @staticmethod
    def gen_random_timestamp():
        """
        Generate a random timestamp in the specified format
        :return:string of timestamp
        """
        year = random.randint(1, 9999)      # Note: With this, there may be future dates
        month = random.randint(1, 12)
        day = random.randint(1, 28)         # Note: With this, there may be fake dates
        hr = random.randint(0, 23)
        minute = random.randint(0, 59)
        sec = random.randint(0, 59)
        timestamp = datetime.datetime(year, month, day, hr, minute, sec, tzinfo=datetime.timezone.utc)
        return timestamp.strftime("%Y-%m-%dT%H:%M:%S+00:00")

    @staticmethod
    def gen_cookies(num_unique=20, max_chars=16, all_same_len=True):
        """
        Generate unique cookies, which num_unique types or number of unique cookies.
        Cookies are by default all 16 chars long, as observed from the task pdf
        :param num_unique: int, number of unique cookies -- default = 20
        :param max_chars: int, number of max chars -- default = 16
        :param all_same_len: boolean, default = True
        :return: list of cookies
        """
        cookie_list = []
        symbols = list(string.ascii_lowercase) + (list(string.ascii_uppercase)) + (list(string.digits))
        for k in range(num_unique):
            if all_same_len:
                cookie = "".join([symbols[random.randint(0, len(symbols)-1)] for i in range(max_chars)])
                cookie_list.append(cookie)
            else:
                chars = random.randint(1, max_chars)
                cookie = "".join([symbols[random.randint(0, len(symbols)-1)] for i in range(chars)])
                cookie_list.append(cookie)
        return cookie_list

    @staticmethod
    def gen_counts(num_unique, num_total_cookies, num_shuffles):
        """
        Given number of unique cookies and total number of cookies, generate number of times a cookie occurs
        :param num_unique: Number of unique cookies
        :param num_total_cookies: Number of total cookies
        :param num_shuffles: How many times we shuffle the data
        :return: list of counts of each cookie
        """
        counts = []
        rem_cookies = num_total_cookies
        for k in range(num_unique):
            if k != num_unique-1:
                add_amount = random.randint(1, math.ceil(rem_cookies // (num_unique - k)))
            else:
                add_amount = rem_cookies
            counts.append(add_amount)
            rem_cookies -= add_amount

        # We do a shuffle technique to flatten the distribution.
        final_counts = counts
        for k in range(num_shuffles):
            random.shuffle(counts)
            final_counts = [final_counts[i] + counts[i] for i in range(len(final_counts))]

        running_total_cookies = 0
        for k in range(num_unique):
            if k != num_unique - 1:
                final_counts[k] = final_counts[k] // (num_shuffles + 1)
                running_total_cookies += final_counts[k]
            else:
                final_counts[k] = num_total_cookies - running_total_cookies

        return final_counts

    @staticmethod
    def gen_dates(counts, num_dates, multiple_max):
        """
        Generate a query. If there are multiple max cookies in that query, make a solution set of multiple max cookie
        indices and the number of times they appear in that query. With this information, build out a dictionary of
        date index --> cookie indices of cookies appearing on that date, with the constraint that there is only a max
        number of times a cookie can appear in the query date, and that the cookies that appear this many times are
        limited by the solution set.
        :param counts: List of counts of the cookies
        :param num_dates: Number of dates to generate cookies for
        :param multiple_max: If there are multiple maxes in the query date
        :return: dates: dictionary of date idx --> cookie indices, query: index of date to be queried,
                 answer: solutions to the query
        """
        counts_loc = counts
        dates = {}
        answer = set()
        query = random.randint(0, num_dates - 2)
        if multiple_max:
            cookies_with_max_number_of_occ = random.sample([i for i in range(len(counts_loc))],
                                                           random.randint(2, len(counts_loc)-1))
            counts_among_cookies_with_max_number_of_occ = [counts_loc[i] for i in cookies_with_max_number_of_occ]
            max_amount_occ = random.randint(1, min(counts_among_cookies_with_max_number_of_occ))
            answer.update(cookies_with_max_number_of_occ)
            dates[query] = []

            for i in cookies_with_max_number_of_occ:
                for k in range(max_amount_occ):
                    dates[query].append(i)
                counts_loc[i] -= max_amount_occ

            # Ensuring that no date is blank
            for i in range(num_dates):
                if i != query:
                    dates[i] = []
                    for j in range(len(counts_loc)):
                        if counts_loc[j] != 0:
                            dates[i].append(j)
                            break

            # Add "noise" or data that is not part of answers to the query with the multiple max
            for i in range(len(counts_loc)):
                if i not in cookies_with_max_number_of_occ:
                    random_num_occ_in_query = random.randint(0, min(max_amount_occ-1, counts_loc[i]))
                    for k in range(random_num_occ_in_query):
                        dates[query].append(i)
                    counts_loc[i] -= random_num_occ_in_query

            for i in range(num_dates):
                if i != query and i != num_dates - 1:
                    for j in range(len(counts_loc)):
                        random_num_occ = random.randint(0, counts_loc[j])
                        for k in range(random_num_occ):
                            dates[i].append(j)
                        counts_loc[j] -= random_num_occ
                elif i == num_dates - 1:            # Add all remaining
                    for j in range(len(counts_loc)):
                        if counts_loc[j] != 0:
                            for k in range(counts_loc[j]):
                                dates[i].append(j)
                            counts_loc[j] = 0
        else:
            cookie_with_max_number_of_occ = random.randint(0, len(counts_loc)-1)
            max_amount_occ = random.randint(1, counts_loc[cookie_with_max_number_of_occ])
            answer.add(cookie_with_max_number_of_occ)
            dates[query] = []

            for k in range(max_amount_occ):
                dates[query].append(cookie_with_max_number_of_occ)
            counts_loc[cookie_with_max_number_of_occ] -= max_amount_occ

            # Ensuring that no date is blank
            for i in range(num_dates):
                if i != query:
                    dates[i] = []
                    for j in range(len(counts_loc)):
                        if counts_loc[j] != 0:
                            dates[i].append(j)
                            break

            # Add "noise" or data that is not part of answers to the query with the multiple max
            for i in range(len(counts_loc)):
                if i != cookie_with_max_number_of_occ:
                    random_num_occ_in_query = random.randint(0, min(max_amount_occ-1, counts_loc[i]))
                    for k in range(random_num_occ_in_query):
                        dates[query].append(i)
                    counts_loc[i] -= random_num_occ_in_query

            for i in range(num_dates):
                if i != query and i != num_dates - 1:
                    for j in range(len(counts_loc)):
                        random_num_occ = random.randint(0, counts_loc[j])
                        for k in range(random_num_occ):
                            dates[i].append(j)
                        counts_loc[j] -= random_num_occ
                elif i == num_dates - 1:            # Add all remaining
                    for j in range(len(counts_loc)):
                        if counts_loc[j] != 0:
                            for k in range(counts_loc[j]):
                                dates[i].append(j)
                            counts_loc[j] = 0

        return dates, query, answer

    @staticmethod
    def convert_to_csv(data):
        """
        Write the CSV given a list of lists, each nested list is a row of CSV
        :param data: list of lists
        :return: void
        """
        with open("test.csv", "w") as test_file:
            csv_writer = csv.writer(test_file)
            csv_writer.writerow(["cookie", "timestamp"])
            for row in data:
                csv_writer.writerow(row)


class CookieProcessorTester(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = ProducingData()

    def test_standard(self):
        """
        Tests standard sized dataset, with default values
        :return: void
        """
        cookie_processor = CookieProcessor()
        query, solution = self.data.gen_test_data()
        cookie_processor.process_cookies_csv("test.csv")
        self.assertEqual(solution, cookie_processor.find_active_cookies(query))

    def test_medium_dataset_standard(self):
        """
        Tests a medium-sized dataset, with default values
        :return: void
        """
        cookie_processor = CookieProcessor()
        query, solution = self.data.gen_test_data(num_dates=50, num_unique_cookies=50, num_total_cookies=1000)
        cookie_processor.process_cookies_csv("test.csv")
        self.assertEqual(solution, cookie_processor.find_active_cookies(query))

    def test_large_dataset_standard(self):
        """
        Tests a large-sized dataset, with default values
        :return: void
        """
        cookie_processor = CookieProcessor()
        query, solution = self.data.gen_test_data(num_dates=500, num_unique_cookies=500, num_total_cookies=25000)
        cookie_processor.process_cookies_csv("test.csv")
        self.assertEqual(solution, cookie_processor.find_active_cookies(query))

    def test_large_dataset_nonexistent_query(self):
        """
        Tests a large-sized dataset, querying a date without cookies
        :return: void
        """
        cookie_processor = CookieProcessor()
        query, solution = self.data.gen_test_data(num_dates=500, num_unique_cookies=500, num_total_cookies=25000,
                                                  exists=False)
        cookie_processor.process_cookies_csv("test.csv")
        self.assertEqual(solution, cookie_processor.find_active_cookies(query))

    def test_large_dataset_multiple_maxes(self):
        """
        Tests a large-sized dataset, querying a date with multiple max occurrence cookies
        :return: void
        """
        cookie_processor = CookieProcessor()
        query, solution = self.data.gen_test_data(num_dates=500, num_unique_cookies=500, num_total_cookies=25000,
                                                  multiple_max=True)
        cookie_processor.process_cookies_csv("test.csv")
        self.assertEqual(solution, cookie_processor.find_active_cookies(query))

    def test_very_large_dataset_standard(self):
        """
        Tests a very large-sized dataset, with default values
        :return: void
        """
        cookie_processor = CookieProcessor()
        query, solution = self.data.gen_test_data(num_dates=1000, num_unique_cookies=1000, num_total_cookies=250000)
        cookie_processor.process_cookies_csv("test.csv")
        self.assertEqual(solution, cookie_processor.find_active_cookies(query))

    def test_very_large_dataset_nonexistent_query(self):
        """
        Tests a large-sized dataset, querying a date without cookies
        :return: void
        """
        cookie_processor = CookieProcessor()
        query, solution = self.data.gen_test_data(num_dates=1000, num_unique_cookies=1000, num_total_cookies=250000,
                                                  exists=False)
        cookie_processor.process_cookies_csv("test.csv")
        self.assertEqual(solution, cookie_processor.find_active_cookies(query))

    def test_very_large_dataset_multiple_maxes(self):
        """
        Tests a very large-sized dataset, querying a date with multiple max occurrence cookies
        :return: void
        """
        cookie_processor = CookieProcessor()
        query, solution = self.data.gen_test_data(num_dates=1000, num_unique_cookies=1000, num_total_cookies=250000,
                                                  multiple_max=True)
        cookie_processor.process_cookies_csv("test.csv")
        self.assertEqual(solution, cookie_processor.find_active_cookies(query))

    def test_iteratively_all(self, iter=5):
        """
        Iteratively test all tests. This generates a new test.csv or test dataset for each run according to params
        fed into it. This makes testing more rigorous.
        :param iter: Number of iterations
        :return: void
        """
        for i in range(iter):
            self.test_standard()
            self.test_medium_dataset_standard()
            self.test_large_dataset_standard()
            self.test_large_dataset_nonexistent_query()
            self.test_large_dataset_multiple_maxes()
            self.test_very_large_dataset_standard()
            self.test_very_large_dataset_nonexistent_query()
            self.test_very_large_dataset_multiple_maxes()


if __name__ == "__main__":
    unittest.main()
