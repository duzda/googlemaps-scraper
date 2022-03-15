# -*- coding: utf-8 -*-
from googlemaps import GoogleMapsScraper
from datetime import datetime, timedelta
import argparse
import csv
from termcolor import colored
import time


ind = {'most_relevant' : 0 , 'newest' : 1, 'highest_rating' : 2, 'lowest_rating' : 3 }
HEADER = ['id_review', 'caption', 'relative_date', 'retrieval_date', 'rating', 'username', 'n_review_user', 'n_photo_user', 'url_user']
HEADER_W_SOURCE = ['id_review', 'caption', 'relative_date','retrieval_date', 'rating', 'username', 'n_review_user', 'n_photo_user', 'url_user', 'url_source']
HEADER_PLACES = ['overall_rating', 'n_reviews', 'url_source']

def csv_writer(header, outfile, path='data/'):
    targetfile = open(path + outfile, mode='w', encoding='utf-8', newline='\n')
    writer = csv.writer(targetfile, quoting=csv.QUOTE_MINIMAL)

    writer.writerow(header)

    return writer

def csv_writer_places(outfile, path='data/'):
    return csv_writer(HEADER_PLACES, outfile, path=path)

def csv_writer_reviews(outfile, source_field, path='data/'):
    return csv_writer(HEADER_W_SOURCE if source_field else HEADER, outfile, path);

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Google Maps reviews scraper.')
    parser.add_argument('--N', type=int, default=100, help='Number of reviews to scrape')
    parser.add_argument('--i', type=str, default='urls.txt', help='target URLs file')
    parser.add_argument('--sort_by', type=str, default='newest', help='most_relevant, newest, highest_rating or lowest_rating')
    parser.add_argument('--place', dest='place', action='store_true', help='Scrape place metadata')
    parser.add_argument('--debug', dest='debug', action='store_true', help='Run scraper using browser graphical interface')
    parser.add_argument('--source', dest='source', action='store_true', help='Add source url to CSV file (for multiple urls in a single file)')
    parser.set_defaults(place=False, debug=False, source=False)

    args = parser.parse_args()

    # store reviews in CSV file
    writer = csv_writer_reviews('reviews.csv', args.source)
    places_writer = csv_writer_places('places.csv')

    with GoogleMapsScraper(debug=args.debug) as scraper:
        with open(args.i, 'r') as urls_file:
            for url in urls_file:
                n_of_all_reviews = 0

                if args.place:
                    data = scraper.get_account(url)
                    row_data = list(data.values())
                    n_of_all_reviews = row_data[1]
                    row_data.append(url[:-1])
                    places_writer.writerow(row_data)

                error = scraper.sort_by(url, ind[args.sort_by])

                if error == 0:

                    n = 0

                    #if ind[args.sort_by] == 0:
                    #    scraper.more_reviews()

                    # if n is less than the number of wanted reviews, or there are no reviews left
                    while n < args.N or n < n_of_all_reviews:

                        # logging to std out
                        print(colored('[Review ' + str(n) + ']', 'cyan'))

                        reviews = scraper.get_reviews(n)
                        if len(reviews) == 0:
                            break

                        for r in reviews:
                            row_data = list(r.values())
                            if args.source:
                                row_data.append(url[:-1])

                            writer.writerow(row_data)

                        n += len(reviews)
