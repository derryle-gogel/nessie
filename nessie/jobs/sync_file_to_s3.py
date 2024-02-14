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

from botocore.exceptions import ClientError as BotoClientError, ConnectionError as BotoConnectionError
from flask import current_app as app
from nessie.externals import s3
from nessie.jobs.background_job import BackgroundJob
from nessie.lib.metadata import create_canvas_snapshot, update_canvas_sync_status

"""Logic for file sync to S3."""


class SyncFileToS3(BackgroundJob):

    # Disable default status logging, since more fine-grained logging is incorporated into the run method.
    status_logging_enabled = False

    def run(self, url, key, canvas_sync_job_id=None):
        if canvas_sync_job_id:
            update_canvas_sync_status(canvas_sync_job_id, key, 'started')
        if s3.object_exists(key):
            app.logger.info(f'Key {key} exists, skipping upload')
            if canvas_sync_job_id:
                update_canvas_sync_status(canvas_sync_job_id, key, 'duplicate')
            return False
        else:
            app.logger.info(f'Key {key} does not exist, starting upload')
            try:

                def update_streaming_status(headers):
                    update_canvas_sync_status(canvas_sync_job_id, key, 'streaming', source_size=headers.get('Content-Length'))

                response = s3.upload_from_url(url, key, on_stream_opened=update_streaming_status)
                if response and canvas_sync_job_id:
                    destination_size = response.get('ContentLength')
                    update_canvas_sync_status(canvas_sync_job_id, key, 'complete', destination_size=destination_size)
                    create_canvas_snapshot(key, size=destination_size)
                return True
            except (BotoClientError, BotoConnectionError, ValueError) as e:
                if canvas_sync_job_id:
                    update_canvas_sync_status(canvas_sync_job_id, key, 'error', details=str(e))
                return False
