CREATE OR REPLACE FUNCTION PSQM.insert_transaction (
    p_pkg        IN NUMBER DEFAULT NULL,
    p_partno     IN VARCHAR2 DEFAULT NULL,
    p_qty        IN NUMBER DEFAULT NULL,
    p_supplier   IN VARCHAR2 DEFAULT NULL,
    p_mvtp       IN VARCHAR2 DEFAULT NULL,
    p_from_loc   IN VARCHAR2 DEFAULT NULL,
    p_to_loc     IN VARCHAR2 DEFAULT NULL,
    p_userid     IN VARCHAR2 DEFAULT NULL,
    p_dn         IN VARCHAR2 DEFAULT NULL,
    p_sn         IN VARCHAR2 DEFAULT NULL)
    RETURN NUMBER
IS
    retVar   NUMBER;
    v_proc   VARCHAR2 (30) := 'INSERT_TRANSACTION';
/******************************************************************************
   NAME:       insert_transaction
   PURPOSE:    Use this function to insert transaction history.

   REVISIONS:
   Ver        Date        Author           Description
   ---------  ----------  ---------------  ------------------------------------
   1.0        4/19/2020   CYANG44       1. Created this function.

   NOTES:

   Automatically available Auto Replace Keywords:
      Object Name:     insert_transaction
      Sysdate:         4/19/2020
      Date and Time:   4/19/2020, 11:07:58 AM, and 4/19/2020 11:07:58 AM
      Username:        CYANG44 (set in TOAD Options, Procedure Editor)
      Table Name:       (set in the "New PL/SQL Object" dialog)

       Return Code defination:
       0: success;
       1: input parameter is not correct;
       2: other exception, check z_mid_log table

******************************************************************************/
BEGIN
    retVar := 0;
    logger (
        'INFO',
           v_proc
        || ' started at '
        || TO_CHAR (SYSDATE, 'yyyy-mm-dd hh24:mi:ss'),
        v_proc,
        p_userid);

    IF    p_partno IS NULL
       OR p_qty IS NULL
       OR p_mvtp IS NULL
       OR (p_to_loc IS NULL and p_from_loc is NULL)
       OR p_userid IS NULL
    THEN
        logger ('ERROR',
                'input parameter is not completed',
                v_proc,
                p_userid);
        retVar := 1;
        RETURN retVar;
    END IF;

    INSERT INTO transactions (sys_timestamp,
                              package_id,
                              partno,
                              qty,
                              supplier_id,
                              movement_type,
                              from_loc,
                              to_loc,
                              userid,
                              dn,
                              serial_no,
                              seq)
         VALUES (SYSDATE,
                 p_pkg,
                 p_partno,
                 p_qty,
                 p_supplier,
                 p_mvtp,
                 p_from_loc,
                 p_to_loc,
                 p_userid,
                 p_dn,
                 p_sn,
                 transaction_seq.nextval);

    COMMIT;
    RETURN retVar;
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
            || v_proc
            || ', the input parameter is:'
            || p_pkg
            || '/'
            || p_partno
            || '/'
            || p_qty
            || '/'
            || p_supplier
            || '/'
            || p_mvtp
            || '/'
            || p_from_loc
            || '/'
            || p_to_loc
            || '/'
            || p_userid
            || '/'
            || p_dn,
            v_proc,
            'PSQM');           -- Consider logging the error and then re-raise
        RAISE;
        retVar := 2;
        RETURN retVar;
END insert_transaction;
/