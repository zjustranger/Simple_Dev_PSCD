CREATE OR REPLACE FUNCTION PSQM.GR_CHECK_new (
    p_user       IN VARCHAR2 DEFAULT NULL,
    p_partno     IN VARCHAR2 DEFAULT NULL,
    p_qty        IN NUMBER,
    p_supplier   IN VARCHAR2 DEFAULT NULL,
    p_due_date   IN VARCHAR2 DEFAULT NULL,
    p_sn         IN VARCHAR2 DEFAULT NULL)
    RETURN NUMBER
IS
    retVar   NUMBER;
    v_cnt    NUMBER;
    /******************************************************************************
       NAME:       GR_CHECK
       PURPOSE:    Use this function to do the GR check before processing.

       REVISIONS:
       Ver        Date        Author           Description
       ---------  ----------  ---------------  ------------------------------------
       1.0        4/17/2020   CYANG44       1. Created this function.
       1.1        5/28/2020   CYANG44       2. Add the input parameter p_qty, due to serial no management requires GR one by one.

       NOTES:

       Automatically available Auto Replace Keywords:
          Object Name:     GR_CHECK
          Sysdate:         4/17/2020
          Date and Time:   4/17/2020, 8:59:21 AM, and 4/17/2020 8:59:21 AM
          Username:        CYANG44 (set in TOAD Options, Procedure Editor)
          Table Name:       (set in the "New PL/SQL Object" dialog)

       Return Code defination:
       0: success;
       1: no input operator id;
       2: no input partno or partno is not correct or partno is invalid;
       3: supplier is null;
       4: supplier and partno mismatch;
       5: supplier master data haven't been maintained;
       6: cannot GR due to this part requires warrenty management but no shelf life info input;
       7: no serial no.
       8: duplicated SN.
       9: part requires serial no management but gr qty <> 1

    ******************************************************************************/

    v_proc   VARCHAR2 (30) := 'GR_CHECK';
BEGIN
    retVar := 0;
    logger (
        'INFO',
           v_proc
        || ' started at '
        || TO_CHAR (SYSDATE, 'yyyy-mm-dd hh24:mi:ss'),
        v_proc,
        p_user);

    -- check if input user is NULL
    IF p_user IS NULL OR p_user = ''
    THEN
        logger ('ERROR',
                'No Operator ID!',
                v_proc,
                USER);
        retVar := 1;
        RETURN retVar;
    --    ELSE
    --        retVar := 0;
    END IF;

    -- check if partno exists
    SELECT COUNT (1)
      INTO v_cnt
      FROM parts
     WHERE partno = p_partno AND invalid_flag IS NULL;

    IF v_cnt = 0
    THEN
        logger (
            'ERROR',
               'Error in partno check: input partno is NULL or no this partno:'
            || p_partno
            || ' or partno is invalid',
            v_proc,
            p_user);
        retVar := 2;
        RETURN retVar;
    END IF;

    -- check if input supplier is NULL
    IF p_supplier IS NULL OR p_supplier = ''
    THEN
        logger ('ERROR',
                'No supplier info',
                v_proc,
                p_user);
        retVar := 3;
        RETURN retVar;
    ELSE
        -- check if this partno is from this supplier
        SELECT COUNT (1)
          INTO v_cnt
          FROM parts
         WHERE partno = p_partno AND supplier_id = p_supplier;

        IF v_cnt = 0
        THEN
            logger (
                'ERROR',
                   'The partno: '
                || p_partno
                || ' is not from supplier: '
                || p_supplier,
                v_proc,
                p_user);
            retVar := 4;
            RETURN retVar;
        ELSE
            -- check if this supplier exists
            SELECT COUNT (1)
              INTO v_cnt
              FROM supplier
             WHERE supplier_id = p_supplier;

            IF v_cnt = 0
            THEN
                logger ('ERROR',
                        'No supplier master data for ' || p_supplier,
                        v_proc,
                        p_user);
                retVar := 5;
                RETURN retVar;
            END IF;
        END IF;
    END IF;

    IF p_due_date IS NULL
    THEN
        SELECT COUNT (1)
          INTO v_cnt
          FROM parts
         WHERE partno = p_partno AND chem_flag = 'X';

        IF v_cnt = 1
        THEN
            logger (
                'ERROR',
                'Cannot GR without warrenty data, due to this partno requires shelf life management.',
                v_proc,
                p_user);
            retVar := 6;
            RETURN retVar;
        END IF;
    END IF;

    IF p_sn IS NULL
    THEN
        logger ('ERROR',
                'No serial number.',
                v_proc,
                p_user);
        retVar := 7;
        RETURN retVar;
    END IF;

    SELECT COUNT (1)
      INTO v_cnt
      FROM scanned_goods
     WHERE serial_no = p_sn AND reversed <> 'Y';

    IF v_cnt <> 0
    THEN
        logger ('ERROR',
                'Duplicated Serial Number that has already finished GR.',
                v_proc,
                p_user);
        retVar := 8;
        RETURN retVar;
    END IF;

    SELECT COUNT (1)
      INTO v_cnt
      FROM parts
     WHERE partno = p_partno AND serial_flag = 'X';

    IF v_cnt = 1 AND p_qty <> 1
    THEN
        logger ('ERROR',
                'part requires serial no but GR qty <> 1',
                v_proc,
                p_user);
        retVar := 9;
        RETURN retVar;
    END IF;


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
            || p_user
            || '/'
            || p_partno
            || '/'
            || p_supplier
            || '/'
            || p_due_date,
            v_proc,
            'PSQM');           -- Consider logging the error and then re-raise
        RAISE;
END GR_CHECK_new;
/