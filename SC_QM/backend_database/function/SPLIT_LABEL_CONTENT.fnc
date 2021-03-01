CREATE OR REPLACE FUNCTION PSQM.split_label_content (p_label      IN     VARCHAR2,
                                                p_partno        OUT VARCHAR2,
                                                p_qty           OUT NUMBER,
                                                p_supplier      OUT VARCHAR2,
                                                p_dn            OUT VARCHAR2,
                                                p_sn            OUT VARCHAR2,
                                                p_md            OUT VARCHAR2,
                                                p_dd            OUT VARCHAR2)
    RETURN NUMBER
IS
    retVar        NUMBER;
    /******************************************************************************
       NAME:       split_label_content
       PURPOSE:    using this function to split label content from QR code.

       REVISIONS:
       Ver        Date        Author           Description
       ---------  ----------  ---------------  ------------------------------------
       1.0        4/19/2020   CYANG44       1. Created this function.

       NOTES:

       Automatically available Auto Replace Keywords:
          Object Name:     split_label_content
          Sysdate:         4/19/2020
          Date and Time:   4/19/2020, 1:02:22 PM, and 4/19/2020 1:02:22 PM
          Username:        CYANG44 (set in TOAD Options, Procedure Editor)
          Table Name:       (set in the "New PL/SQL Object" dialog)

       Function spec:
       1. the label content is a string, with '|' seperate the content in the label, and also end with '|'. below is an example:
        |P|66666666|Q|100|V|TEST1|N|20200419|S|QT999|M|20200301|
            |p| -> partno: 66666666;
            |Q| -> qty: 100;
            |V| -> supplier: TEST1;
            |N| -> dispatch note: 20200419
            |S| -> serial no: QT999 (this field is defined as a varchar2 data, so both letter and number are allowed, but should be considered the regulation later.)
            |M| -> manufaturing date: 20200301 (8 digits yyyymmdd)
            |D| -> due date: yyyymmdd (8 digits represent the due date incase some supplier only offer due date instead of manufaturing date)
       2. the function input with a long string from label content, and output the split result in sequence to several output parameters.

    ******************************************************************************/
    v_procedure   VARCHAR2 (30) := 'SPLIT_LABEL_CONTENT';
BEGIN
    retVar := 0;
    logger (
        'INFO',
           v_procedure
        || ' started at '
        || TO_CHAR (SYSDATE, 'yyyy-mm-dd hh24:mi:ss'),
        v_procedure,
        'PSQM');

    -- check if input label is NULL
    IF p_label IS NULL OR p_label = ''
    THEN
        logger ('ERROR',
                'Input label content is NULL',
                v_procedure,
                'PSQM');
        retVar := 1;
        RETURN retVar;
    --    ELSE
    --        retVar := 0;
    END IF;

    SELECT SUBSTR (p_label,
                   INSTR (p_label, '|P|') + 3,
                     INSTR (p_label,
                            '|',
                            INSTR (p_label, '|P|'),
                            3)
                   - INSTR (p_label, '|P|')
                   - 3)
      INTO p_partno
      FROM DUAL;

    SELECT SUBSTR (p_label,
                   INSTR (p_label, '|Q|') + 3,
                     INSTR (p_label,
                            '|',
                            INSTR (p_label, '|Q|'),
                            3)
                   - INSTR (p_label, '|Q|')
                   - 3)
      INTO p_qty
      FROM DUAL;

    SELECT SUBSTR (p_label,
                   INSTR (p_label, '|V|') + 3,
                     INSTR (p_label,
                            '|',
                            INSTR (p_label, '|V|'),
                            3)
                   - INSTR (p_label, '|V|')
                   - 3)
      INTO p_supplier
      FROM DUAL;

    SELECT SUBSTR (p_label,
                   INSTR (p_label, '|N|') + 3,
                     INSTR (p_label,
                            '|',
                            INSTR (p_label, '|N|'),
                            3)
                   - INSTR (p_label, '|N|')
                   - 3)
      INTO p_dn
      FROM DUAL;

    SELECT SUBSTR (p_label,
                   INSTR (p_label, '|S|') + 3,
                     INSTR (p_label,
                            '|',
                            INSTR (p_label, '|S|'),
                            3)
                   - INSTR (p_label, '|S|')
                   - 3)
      INTO p_sn
      FROM DUAL;

    SELECT SUBSTR (p_label,
                   INSTR (p_label, '|M|') + 3,
                     INSTR (p_label,
                            '|',
                            INSTR (p_label, '|M|'),
                            3)
                   - INSTR (p_label, '|M|')
                   - 3)
      INTO p_md
      FROM DUAL;

    SELECT SUBSTR (p_label,
                   INSTR (p_label, '|D|') + 3,
                     INSTR (p_label,
                            '|',
                            INSTR (p_label, '|D|'),
                            3)
                   - INSTR (p_label, '|D|')
                   - 3)
      INTO p_dd
      FROM DUAL;

    logger (
        'INFO',
           'Split successfully!, the output is: '
        || 'Partno:'
        || p_partno
        || '/Qty:'
        || p_qty
        || '/Supplier:'
        || p_supplier
        || '/Dispatch Note:'
        || p_dn
        || '/Serial No:'
        || p_sn
        || '/Manufacturing Date:'
        || p_md
        || '/Due Date:'
        || p_dd,
        v_procedure,
        'PSQM');

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
            || v_procedure
            || ', the input parameter is:'
            || p_label,
            v_procedure,
            'PSQM');           -- Consider logging the error and then re-raise
        RAISE;
END split_label_content;
/