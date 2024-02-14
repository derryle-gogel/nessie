"""
Copyright ©2024. The Regents of the University of California (Regents). All Rights Reserved.

Permission to use, copy, modify, and distribute this software and its documentation
for educational, research, and not-for-profit purposes, without fee and without a
signed licensing agreement, is hereby granted, provided that the above copyright
notice, this paragraph and the following two paragraphs appear in all copies,
modifications, and distributions.

Contact The Office of Technology Licensing, UC Berkeley, 2150 Shattuck Avenue,
Suite 510, Berkeley, CA 94720-1620, (510) 643-7201, otl@berkeley.edu,
http://ipira.berkeley.edu/industry-info for commercial licensing opportunities.

IN NO EVENT SHALL REGENTS BE LIABLE TO ANY PARTY FOR DIRECT, INDIRECT, SPECIAL,
INCIDENTAL, OR CONSEQUENTIAL DAMAGES, INCLUDING LOST PROFITS, ARISING OUT OF
THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN IF REGENTS HAS BEEN ADVISED
OF THE POSSIBILITY OF SUCH DAMAGE.

REGENTS SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. THE
SOFTWARE AND ACCOMPANYING DOCUMENTATION, IF ANY, PROVIDED HEREUNDER IS PROVIDED
"AS IS". REGENTS HAS NO OBLIGATION TO PROVIDE MAINTENANCE, SUPPORT, UPDATES,
ENHANCEMENTS, OR MODIFICATIONS.
"""

import tempfile

from flask import current_app as app
from nessie.externals import s3
from nessie.jobs.background_job import BackgroundJob
from nessie.lib.metadata import update_background_job_status
from nessie.lib.util import get_s3_piazza_data_path

"""Logic for transforming Piazza API data into Spark-parsable JSON."""


class TransformPiazzaApiData(BackgroundJob):

    def run(self, archive=None):
        frequency, datestamp, archive, s3_source = get_s3_piazza_data_path(archive)

        s3_dest = app.config['LOCH_S3_PIAZZA_DATA_PATH'] + '/transformed'

        app.logger.info(f'Starting Piazza API data transform job... {s3_source} > {s3_dest}')
        message = self.transform(s3_source, s3_dest, self.job_id)
        app.logger.info('Piazza data transform complete.')
        return f'{s3_source}: {message}'

    def transform(self, s3_source, s3_dest, job_id):
        objects = s3.get_keys_with_prefix(s3_source)
        if len(objects) == 0:
            message = f'Zero objects found in {s3_source}. Quitting.'
            app.logger.info(message)
            return message
        app.logger.info(f'Will transform {len(objects)} objects from {s3_source} and put results to {s3_dest}.')
        objects_updated = 0
        new_objects = 0
        objects_in_error = 0
        total_objects = 0
        for o in objects:
            file_name = o.split('/')[-1]
            app.logger.debug(f'processing {file_name}')
            # file_name is like 'daily_2020-08-14.zip'
            piazza_zip_file = s3.get_object_compressed_text_reader(o)
            for subfile in piazza_zip_file.namelist():
                if '.json' in subfile:
                    try:
                        json_file = subfile.split('/')[-1]
                        course_id = subfile.split('/')[-2]
                        file_type = json_file.split('_')[0]
                        record = piazza_zip_file.read(subfile)
                        with tempfile.TemporaryFile() as result:
                            s3_object = f'{s3_dest}/{file_type}/{course_id}/{json_file}'
                            if s3.object_exists(s3_object):
                                objects_updated += 1
                            else:
                                new_objects += 1
                            result.write(record)
                            s3.upload_file(result, s3_object)
                            total_objects += 1
                        # update job queue every 1000 files...
                        if total_objects % 1000 == 0:
                            message = f'{subfile}, {total_objects} so far; ' \
                                      + f'{new_objects} new files; ' \
                                      + f'{objects_updated} existing files. {objects_in_error} files in error' \
                                      + f'({len(objects)} objects in all)'
                            update_background_job_status(job_id, 'transforming', details=message)
                    except Exception as e:
                        app.logger.error(f'could not extract {subfile}')
                        app.logger.error(e)
                        objects_in_error += 1
                else:
                    # not a json file, so we skip it
                    continue
        message = f'Transformed {len(objects)} input files; created {new_objects} new objects; '\
                  + f'updated {objects_updated} existing objects. {objects_in_error} objects in error'
        app.logger.info(message)
        return message
