/**
 * Copyright ©2023. The Regents of the University of California (Regents). All Rights Reserved.
 *
 * Permission to use, copy, modify, and distribute this software and its documentation
 * for educational, research, and not-for-profit purposes, without fee and without a
 * signed licensing agreement, is hereby granted, provided that the above copyright
 * notice, this paragraph and the following two paragraphs appear in all copies,
 * modifications, and distributions.
 *
 * Contact The Office of Technology Licensing, UC Berkeley, 2150 Shattuck Avenue,
 * Suite 510, Berkeley, CA 94720-1620, (510) 643-7201, otl@berkeley.edu,
 * http://ipira.berkeley.edu/industry-info for commercial licensing opportunities.
 *
 * IN NO EVENT SHALL REGENTS BE LIABLE TO ANY PARTY FOR DIRECT, INDIRECT, SPECIAL,
 * INCIDENTAL, OR CONSEQUENTIAL DAMAGES, INCLUDING LOST PROFITS, ARISING OUT OF
 * THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN IF REGENTS HAS BEEN ADVISED
 * OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 * REGENTS SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. THE
 * SOFTWARE AND ACCOMPANYING DOCUMENTATION, IF ANY, PROVIDED HEREUNDER IS PROVIDED
 * "AS IS". REGENTS HAS NO OBLIGATION TO PROVIDE MAINTENANCE, SUPPORT, UPDATES,
 * ENHANCEMENTS, OR MODIFICATIONS.
 */


DROP TABLE IF EXISTS {rds_schema_sis_internal}.edo_enrollments CASCADE;

CREATE TABLE IF NOT EXISTS {rds_schema_sis_internal}.edo_enrollments
(
    sis_term_id VARCHAR,
    sis_section_id VARCHAR,
    ldap_uid VARCHAR,
    sis_enrollment_status VARCHAR,
    units DOUBLE PRECISION,
    grading_basis VARCHAR,
    grade VARCHAR,
    grade_midterm VARCHAR
);

INSERT INTO {rds_schema_sis_internal}.edo_enrollments (
  SELECT *
  FROM dblink('{rds_dblink_to_redshift}',$REDSHIFT$
    SELECT sis_term_id, sis_section_id, ldap_uid, sis_enrollment_status, units, grading_basis,
      grade, grade_midterm
    FROM {redshift_schema_sisedo_internal}.enrollments
  $REDSHIFT$)
  AS redshift_edo_enrollments (
    sis_term_id VARCHAR,
    sis_section_id VARCHAR,
    ldap_uid VARCHAR,
    sis_enrollment_status VARCHAR,
    units DOUBLE PRECISION,
    grading_basis VARCHAR,
    grade VARCHAR,
    grade_midterm VARCHAR
  )
);

CREATE INDEX idx_edo_enrollments_term_id_section_id ON {rds_schema_sis_internal}.edo_enrollments(sis_term_id, sis_section_id);
CREATE INDEX idx_edo_enrollments_ldap_uid ON {rds_schema_sis_internal}.edo_enrollments(ldap_uid);

DROP TABLE IF EXISTS {rds_schema_sis_internal}.edo_sections CASCADE;

CREATE TABLE IF NOT EXISTS {rds_schema_sis_internal}.edo_sections
(
    sis_term_id VARCHAR,
    sis_section_id VARCHAR,
    is_primary BOOLEAN,
    sis_course_name VARCHAR,
    sis_course_title VARCHAR,
    sis_instruction_format VARCHAR,
    sis_section_num VARCHAR,
    cs_course_id VARCHAR,
    session_code VARCHAR,
    instruction_mode VARCHAR,
    instructor_uid VARCHAR,
    instructor_name VARCHAR,
    instructor_role_code VARCHAR,
    meeting_location VARCHAR,
    meeting_days VARCHAR,
    meeting_start_time VARCHAR,
    meeting_end_time VARCHAR,
    meeting_start_date VARCHAR,
    meeting_end_date VARCHAR,
    enrollment_count INTEGER,
    enroll_limit INTEGER,
    waitlist_limit INTEGER
);

INSERT INTO {rds_schema_sis_internal}.edo_sections (
  SELECT *
  FROM dblink('{rds_dblink_to_redshift}',$REDSHIFT$
    SELECT sis_term_id, sis_section_id, is_primary, sis_course_name, sis_course_title, sis_instruction_format,
      sis_section_num, cs_course_id, session_code, instruction_mode,
      instructor_uid, instructor_name, instructor_role_code, meeting_location,
      meeting_days, meeting_start_time, meeting_end_time, meeting_start_date, meeting_end_date,
      enrollment_count, enroll_limit, waitlist_limit
    FROM {redshift_schema_sisedo_internal}.sections
  $REDSHIFT$)
  AS redshift_edo_sections (
    sis_term_id VARCHAR,
    sis_section_id VARCHAR,
    is_primary BOOLEAN,
    sis_course_name VARCHAR,
    sis_course_title VARCHAR,
    sis_instruction_format VARCHAR,
    sis_section_num VARCHAR,
    cs_course_id VARCHAR,
    session_code VARCHAR,
    instruction_mode VARCHAR,
    instructor_uid VARCHAR,
    instructor_name VARCHAR,
    instructor_role_code VARCHAR,
    meeting_location VARCHAR,
    meeting_days VARCHAR,
    meeting_start_time VARCHAR,
    meeting_end_time VARCHAR,
    meeting_start_date VARCHAR,
    meeting_end_date VARCHAR,
    enrollment_count INTEGER,
    enroll_limit INTEGER,
    waitlist_limit INTEGER
  )
);

CREATE INDEX idx_edo_sections_term_id_section_id ON {rds_schema_sis_internal}.edo_sections(sis_term_id, sis_section_id);
