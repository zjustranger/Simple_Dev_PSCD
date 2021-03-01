CREATE OR REPLACE FUNCTION PSQM.request_for_new_child_sn (
    p_sn     IN VARCHAR2,
    p_user   IN VARCHAR2)
    RETURN VARCHAR2
IS
    newSN          VARCHAR2 (30);
    /******************************************************************************
       NAME:       request_for_new_child_sn
       PURPOSE:    use this function to request the new child sn that should be assign to the new split package.
       ALGORITHM:  use a table: downsize_history to track all the split packages relationship. the column: source_sn is used to record the
                   original SN which from GR label, and the column: child_sn is used to track all split child packages' SN. And the column
                   current_seq is used to mark the biggest seq_id for all child packages.
       INPUT:      SN (no matter original SN or child SN, for example: IT0001 or IT0001_CHILD1)
       OUTPUT:     new SN should be named to new split packages. for example, IT0001_CHILD4

       REVISIONS:
       Ver        Date        Author           Description
       ---------  ----------  ---------------  ------------------------------------
       1.0        4/22/2020   CYANG44       1. Created this function.

       NOTES:

       Automatically available Auto Replace Keywords:
          Object Name:     request_for_new_child_sn
          Sysdate:         4/22/2020
          Date and Time:   4/22/2020, 8:46:48 AM, and 4/22/2020 8:46:48 AM
          Username:        CYANG44 (set in TOAD Options, Procedure Editor)
          Table Name:       (set in the "New PL/SQL Object" dialog)

    ******************************************************************************/
    v_procedure    VARCHAR2 (30) := 'request_for_new_child_sn';
    v_cnt_source   NUMBER := 0;
    v_cnt_child    NUMBER := 0;
    v_source_sn    VARCHAR2 (30);
    v_child_sn     VARCHAR2 (30);
    v_seq          INTEGER;
BEGIN
    newSN := '';

    SELECT COUNT (1)
      INTO v_cnt_child
      FROM downsize_history
     WHERE child_sn = p_sn;

    SELECT COUNT (1)
      INTO v_cnt_source
      FROM downsize_history
     WHERE source_sn = p_sn;

    IF v_cnt_child <> 0
    THEN
        SELECT current_seq
          INTO v_seq
          FROM downsize_history
         WHERE child_sn = p_sn;

        SELECT source_sn
          INTO v_source_sn
          FROM downsize_history
         WHERE child_sn = p_sn;

        v_seq := v_seq + 1;
        newSN := v_source_sn || '_CHILD' || v_seq;

        UPDATE downsize_history
           SET current_seq = v_seq
         WHERE source_sn = v_source_sn;

        INSERT INTO downsize_history (source_sn,
                                      current_seq,
                                      sys_timestamp,
                                      child_sn,
                                      userid)
             VALUES (v_source_sn,
                     v_seq,
                     SYSDATE,
                     newSN,
                     p_user);

        COMMIT;
    END IF;

    IF v_cnt_child = 0 AND v_cnt_source = 0
    THEN
        --this is a new source_sn
        newSN := p_sn || '_CHILD1';

        INSERT INTO downsize_history (source_sn,
                                      current_seq,
                                      sys_timestamp,
                                      child_sn,
                                      userid)
             VALUES (p_sn,
                     1,
                     SYSDATE,
                     newSN,
                     p_user);

        COMMIT;
    END IF;

    IF v_cnt_child = 0 AND v_cnt_source <> 0
    THEN
        --this is an old source_sn
        SELECT MAX (current_seq)
          INTO v_seq
          FROM downsize_history
         WHERE source_sn = p_sn;

        v_seq := v_seq + 1;
        newSN := p_sn || '_CHILD' || v_seq;

        UPDATE downsize_history
           SET current_seq = v_seq
         WHERE source_sn = p_sn;

        INSERT INTO downsize_history (source_sn,
                                      current_seq,
                                      sys_timestamp,
                                      child_sn,
                                      userid)
             VALUES (p_sn,
                     v_seq,
                     SYSDATE,
                     newSN,
                     p_user);

        COMMIT;
    END IF;

    logger (
        'INFO',
           'generate new child package SN: '
        || newSN
        || ', the input SN is: '
        || p_sn);
    RETURN newSN;
EXCEPTION
    WHEN NO_DATA_FOUND
    THEN
        NULL;
    WHEN OTHERS
    THEN
        ROLLBACK;
        logger (
            'ERROR',
               DBMS_UTILITY.format_error_backtrace
            || SQLCODE
            || SUBSTR (SQLERRM, 1, 200)
            || '; While running '
            || v_procedure
            || ', the input parameter is:'
            || p_sn,
            v_procedure,
            'PSQM');           -- Consider logging the error and then re-raise
        RAISE;
END request_for_new_child_sn;
/