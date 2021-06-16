#! /usr/bin/python3

import csv
import argparse
import os
import shutil
import datetime
import tarfile
import argparse


DATE = datetime.date.today().isoformat()
BASE_EXPORT_DIRECTORY = "/var/lib/pulp/katello-export/"


# Validates export directory
def validate_export_directory(export_directory):
    print(f"INFO: Validating that the {export_directory} directory exists")
    if not os.path.exists(export_directory):
        os.makedirs(export_directory)


# Creates incremental directory
def create_incremental_directory(export_directory):
    print(f"INFO: Create a directory with todays date in - {export_directory}")
    export_date_directory = os.path.join(export_directory, DATE)
    if os.path.exists(f"{export_date_directory}"):
        print(f"INFO: Removing duplicate directory with the same date - {export_date_directory}")
        shutil.rmtree(f"{export_date_directory}")
    os.mkdir(f"{export_date_directory}")


# Removes stale incremental directories
def remove_stale_data(repository):
    print('INFO: Making sure that there is no stale incremental data')
    repository_base_directory = os.path.join(BASE_EXPORT_DIRECTORY, "".join((repository['GUID'], "-incremental")))
    if os.path.exists(repository_base_directory):
        print(f"INFO: Removing stale directory - {repository_base_directory}")
        shutil.rmtree(repository_base_directory)


# Sync Satellite repository
def sync_repository(repository, organization_id):
    print(f"INFO: Syncing repository - {repository['Repository Name']}")
    os.system(f"hammer repository synchronize --id {repository['ID']} --organization-id {organization_id}")


# Runs the export process for the repository
def run_export(repository, start_date):
    formatted_date = start_date.strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"INFO: Starting export process of repository - {repository['Repository Name']}")
    os.system(f"hammer repository export --id {repository['ID']} --since {formatted_date}")


# Move incremental export to main export directory
def move_export(repository, export_directory):
    source = "".join((os.path.join(BASE_EXPORT_DIRECTORY, repository['GUID']), "-incremental"))
    destination = os.path.join(export_directory, DATE, repository['Repository Name'])
    print(f"INFO: Moving the export directoty from {source} to {destination}")
    shutil.move(source, destination)


# Creates incremental exports of the defined repositories in a csv file
def create_incremental_export(csv_file_name, export_directory, organization_id, start_date):
    with open(csv_file_name, 'r') as csvfile:
        reader = csv.DictReader(csvfile) 
        for repository_def in reader:  
            remove_stale_data(repository_def)
            sync_repository(repository_def, organization_id)
            run_export(repository_def, start_date)
            move_export(repository_def, export_directory)


# Creates a tar archive with all exported repositories
def make_tar_file(output_filename, source_dir):
    print(f"INFO: Archive the {source_dir} export in the {output_filename} tar directory")
    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(source_dir)


def main():
    parser = argparse.ArgumentParser(description="Create an incremental export from satellite")
    parser.add_argument("-s", "--start_date", type=lambda date: datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ"), help="The date from which the incremental sync will be taken" , required=True)
    parser.add_argument("-o","--export_dir", help="The directory used to store the exported repositories", required=True)
    parser.add_argument("-n","--organization_id", type=int, help="The organization from which the repository is taken", required=True)
    parser.add_argument("-i","--csv_file", help="The csv file to create exports from", required=True)

    args = parser.parse_args()

    validate_export_directory(args.export_dir)
    create_incremental_directory(args.export_dir)
    create_incremental_export(args.csv_file , args.export_dir, args.organization_id, args.start_date)
    tar_directory = os.path.join(args.export_dir, DATE)
    tar_file = "".join((tar_directory, ".tar.gz"))
    make_tar_file(tar_file, tar_directory)


if __name__ == '__main__':
    main()
    