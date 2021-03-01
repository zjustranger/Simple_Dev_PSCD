CREATE OR REPLACE PROCEDURE PSQM.feedback_scanning_result (
    p_label       IN     VARCHAR2,
    p_partno         OUT VARCHAR2,
    p_qty            OUT NUMBER,
    p_supplier       OUT VARCHAR2,
    p_dn             OUT VARCHAR2,
    p_sn             OUT VARCHAR2,
    p_md             OUT VARCHAR2,
    p_dd             OUT VARCHAR2,
    p_loc_id         OUT VARCHAR2,
    p_parent_sn      OUT VARCHAR2)
IS
    tmpVar        NUMBER;
    /******************************************************************************
       NAME:       feedback_scanning_result
       PURPOSE:    calculate the real-time info of the scanned label and feedback.

       REVISIONS:
       Ver        Date        Author           Description
       ---------  ----------  ---------------  ------------------------------------
       1.0        4/24/2020   CYANG44       1. Created this procedure.

       NOTES:

       Automatically available Auto Replace Keywords:
          Object Name:     feedback_scanning_result
          Sysdate:         4/24/2020
          Date and Time:   4/24/2020, 10:33:02 AM, and 4/24/2020 10:33:02 AM
          Username:        CYANG44 (set in TOAD Options, Procedure Editor)
          Table Name:       (set in the "New PL/SQL Object" dialog)

    ******************************************************************************/
    v_procedure   VARCHAR2 (30) := 'feedback_scanning_result';

    v_ret         NUMBER := 0;
    v_cnt         NUMBER := 0;
BEGIN
    tmpVar := 0;

    logger ('INFO',
            'procedure start!',
            v_procedure,
            'PSQM');

    --step1. split lable and get sn information
    v_ret :=
        split_label_content (p_label,
                             p_partno,
                             p_qty,
                             p_supplier,
                             p_dn,
                             p_sn,
                             p_md,
                             p_dd);

    IF v_ret <> 0
    THEN
        logger ('ERROR',
                'error in split label content',
                v_procedure,
                'PSQM');
        RETURN;
    END IF;

    --step2. get the real time information of this sn
    SELECT COUNT (1)
      INTO v_cnt
      FROM inventory
     WHERE serial_no = p_sn;

    IF v_cnt = 0
    THEN
        p_partno := NULL;
        p_sn := NULL;
        p_qty := 0;
        p_supplier := NULL;
        p_dn := NULL;
        p_md := NULL;
        p_dd := NULL;
        p_loc_id := NULL;
        p_parent_sn := NULL;
    ELSE
        SELECT partno,
               qty,
               supplier_id,
               dn,
               prod_date,
               due_date
          INTO p_partno,
               p_qty,
               p_supplier,
               p_dn,
               p_md,
               p_dd
          FROM packages
         WHERE serial_no = p_sn;

        SELECT loc_id
          INTO p_loc_id
          FROM inventory
         WHERE serial_no = p_sn;
    END IF;

    --step3. feedback the parent_sn if possible
    SELECT parent_sn
      INTO p_parent_sn
      FROM packages
     WHERE serial_no = p_sn;
EXCEPTION
    WHEN NO_DATA_FOUND
    THEN
        NULL;
    WHEN OTHERS
    THEN
        -- Consider logging the error and then re-raise
        RAISE;
END feedback_scanning_result;
/