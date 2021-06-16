# ssync
A tool for Satellite incremental yum repository sync management for disconnected environments. The tool exports yum repositories incrementally, and places them in a central tar archive. The tool has been developed for Satellite 6.8, and uses Python 3.6 for its runtime environment.

## Prerequisites

* A Satellite server that's connected to the internet.
* Python 3 installed on the connected Satellite server.

```
<satellite-server> $ foreman-maintain packages install python3
```

* Previously synced Satellite repositories. **The tool is used for incremental updates only**.

## CSV

SSYNC depends on a CSV file to function. The CSV file will contain information regarding the repositories that are going to be synced incrementally. An example csv file can be found [here](.satellite.csv). The CSV file structure will follow the next pattern -

Repository Name | ID | GUID
--------------- | -- | ----
Red Hat Enterprise Linux 7 Server - Extras RPMs x86_64 | 4 | 0fc092c8-0040-460e-a338-0f85f49a259b
Red Hat Ansible Engine 2.9 RPMs for Red Hat Enterprise Linux 7 Server x86_64 | 25 | 2be8e514-a786-4c13-a611-b0a6868397a9
Red Hat Enterprise Linux 7 Server Kickstart x86_64 7.9 | 12 | 6823aa52-f63e-47a7-a2f4-9a026349f717

 **Repository Name** - Stands for the repository that's going to be incrementally exported. The output for this value can be found by running the next command on the Satellite server -

 ```
<satellite-server> $ hammer repository list
 ```

 **ID** - Stands for the repositories unique ID in the Satellite server. The output for this value can be found by running the next command on the Satellite server -

 ```
<satellite-server> $ hammer repository list
 ```

 **GUID** - Stands for the unique repository ID for the repository export path. In order to validate the GUID, navigate to `/var/lib/pulp/katello-export/`. You will be able to find the value of the GUID from the directory names placed in the `katello-export` path.

 ```
<satellite-server> $ ls -l /var/lib/pulp/katello-export/
 ```

 ## Usage
ssync uses 4 mandatory parameters -

```
<satellite-server> $ ./ssync.py --help
usage: ssync.py [-h] -s START_DATE -o EXPORT_DIR -n ORGANIZATION_ID -i
                CSV_FILE

Create an incremental export from satellite

optional arguments:
  -h, --help            show this help message and exit
  -s START_DATE, --start_date START_DATE
                        The date from which the incremental sync will be taken
  -o EXPORT_DIR, --export_dir EXPORT_DIR
                        The directory used to store the exported repositories
  -n ORGANIZATION_ID, --organization_id ORGANIZATION_ID
                        The organization from which the repository is taken
  -i CSV_FILE, --csv_file CSV_FILE
                        The csv file to create exports from
```

**--start_date** - Used to indicate from which date the incremental sync should be taken from. For example - 2021-05-25T12:00:00Z (YYYY-MM-DDTHH:MM:SSZ)

**--export_dir** - The directory in which the export will be saved. The directory will be created if not present.

**--organization_id** - The ID of the organization that contains the repositories. The ID can be taken from the next command - `<satellite-server> $ hammer repository list`

**--csv_file** - The CSV files that is going to be used by the tool. The CSV file will contain information regarding the exported repositories.

For example, in order to incrementally sync all the changes in the repositories mentioned in [satellite.csv](./satellite.csv) since the 25th of May 2021. And place the exported archive into the `/tmp/export` directory, you should run the next commands -

```
<satellite-server> $ git clone https://github.com/michaelkotelnikov/ssync.git

<satellite-server> $ cd ssync/

<satellite-server> $ ./ssync.py --start_date 2021-05-25T12:00:00Z --export_dir /tmp/export --organization_id 1 --csv_file satellite.csv
```