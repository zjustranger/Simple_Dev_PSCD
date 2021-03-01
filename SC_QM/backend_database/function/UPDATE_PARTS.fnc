CREATE OR REPLACE FUNCTION PSQM.update_parts (p_partno     IN VARCHAR2,
                                              p_descr      IN VARCHAR2,
                                              p_unit       IN VARCHAR2,
                                              p_min        IN VARCHAR2,
                                              p_max        IN VARCHAR2,
                                              p_warrenty   IN VARCHAR2,
                                              p_supplier   IN VARCHAR2,
                                              p_invalid    IN NUMBER,
                                              p_shelf      IN NUMBER,
                                              p_serial     IN NUMBER,
                                              p_user       IN VARCHAR2)
    RETURN NUMBER
IS
    retVar        NUMBER;
    /******************************************************************************
       NAME:       update_parts
       PURPOSE:    using this function to update parts, check if there are any problems in updating.

       REVISIONS:
       Ver        Date        Author           Description
       ---------  ----------  ---------------  ------------------------------------
       1.0        5/15/2020   CYANG44       1. Created this function.

       NOTES:

       Automatically available Auto Replace Keywords:
          Object Name:     update_parts
          Sysdate:         5/15/2020
          Date and Time:   5/15/2020, 8:09:51 AM, and 5/15/2020 8:09:51 AM
          Username:        CYANG44 (set in TOAD Options, Procedure Editor)
          Table Name:       (set in the "New PL/SQL Object" dialog)

       Return code defination:
       0: successful
       1: general exception that not been caught
       2: partno doesn't exists
       3: part requires shelf life management but no warrenty info maintained
       4:

    ******************************************************************************/
    v_procedure   VARCHAR2 (30) := 'update_parts';
    v_cnt         NUMBER := 0;
BEGIN
    retVar := 1;

    logger (
        'INFO',
           'update_parts starts for partno: '
        || p_partno
        || ', User: '
        || p_user,
        v_procedure,
        p_user);

    --step 1. check if the parts exists.
    SELECT COUNT (1)
      INTO v_cnt
      FROM parts
     WHERE partno = upper(p_partno);

    IF v_cnt = 0
    THEN
        logger ('ERROR',
                'Cannot find partno, so cannot update: ' || p_partno,
                v_procedure,
                p_user);
        retVar := 2;
        RETURN retVar;
    END IF;

    --step 2. check if supplier info exists, otherwise insert new supplier code.
    SELECT COUNT (1)
      INTO v_cnt
      FROM supplier
     WHERE supplier_id = UPPER (p_supplier);

    IF v_cnt = 0
    THEN
        INSERT INTO supplier (supplier_id, language, supplier_descr)
             VALUES (UPPER (p_supplier), 'ZH', '');

        COMMIT;
    END IF;

    --step 3. if partno requires shelf life management, then must maintain the warrenty_day.
    IF p_shelf = 1 AND (p_warrenty = 0 OR p_warrenty IS NULL)
    THEN
        logger (
            'ERROR',
               'Part requires shelf life management but no warrenty info input: '
            || p_partno,
            v_procedure,
            p_user);
        retVar := 3;
        RETURN retVar;
    END IF;

    --step 4. update the parts table.
    UPDATE parts
       SET part_descr = p_descr,
           unit = p_unit,
           min_qty = p_min,
           max_qty = p_max,
           valid_day = p_warrenty,
           supplier_id = UPPER (p_supplier),
           updated_by = p_user,
           update_timestamp = SYSDATE,
           invalid_flag = (CASE WHEN p_invalid = 1 THEN 'X' ELSE '' END),
           chem_flag = (CASE WHEN p_shelf = 1 THEN 'X' ELSE '' END),
           serial_flag = (CASE WHEN p_serial = 1 THEN 'X' ELSE '' END)
     WHERE partno = upper(p_partno);

    COMMIT;

    retVar := 0;
    RETURN retVar;
EXCEPTION
    WHEN OTHERS
    THEN
        logger ('ERROR',
                'Error in updating parts.',
                v_procedure,
                p_user);
        retVar := 1;
        RETURN retVar;         -- Consider logging the error and then re-raise
        RAISE;
END update_parts;
/