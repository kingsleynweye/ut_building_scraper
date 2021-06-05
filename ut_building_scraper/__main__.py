import argparse
import os
import sys
from ut_building_scraper.scrape import Scrape

def main():
    parser = argparse.ArgumentParser(prog='ut_building_scraper',description='Scrape building information from the UT Facilities Services website.')
    parser.add_argument('--version', action='version', version='%(prog)s 0.0.1')
    parser.add_argument('-f','--filepath',default=None,dest='filepath',type=str,help='Filepath to write to.')
    args = parser.parse_args()
    data = Scrape.building_information()

    if args.filepath:
        extension = args.filepath.split('.')[-1]
        directories = '/'.join(args.filepath.split('/')[0:-1])

        if len(directories) > 0:
            os.makedirs(directories,exist_ok=True)
        else:
            pass

        if extension == 'csv':
            data.to_csv(args.filepath,index=False)
        elif extension == 'json':
            data.to_json(args.filepath,indent=4,orient='records')
        else:
            raise Exception(f'Unsupported filetype parsed: .{extension}')
    else:
        print(data.to_json(indent=4,orient='records'))

if __name__ == '__main__':
    sys.exit(main())