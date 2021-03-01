CREATE OR REPLACE PROCEDURE PSQM.GR_Scanning_new (
    p_label      IN     VARCHAR2,
    p_user       IN     VARCHAR2 DEFAULT NULL,
    p_hostname   IN     VARCHAR2 DEFAULT NULL,
    p_ip         IN     VARCHAR2 DEFAULT NULL,
    p_loc_id     IN     VARCHAR2,
    retVar          OUT NUMBER)
IS
    /******************************************************************************
       NAME:       GR_Scanning
       PURPOSE:    This procedure is used to receive the scanning result, check, and call GR procedure.

       REVISIONS:
       Ver        Date        Author           Description
       ---------  ----------  ---------------  ------------------------------------
       1.0        4/20/2020   CYANG44       1. Created this procedure.
       1.1        5/28/2020   CYANG44       2. add the gr qty check for part requires serial no management

       NOTES:

       Automatically available Auto Replace Keywords:
          Object Name:     GR_Scanning
          Sysdate:         4/20/2020
          Date and Time:   4/20/2020, 3:04:57 PM, and 4/20/2020 3:04:57 PM
          Username:        CYANG44 (set in TOAD Options, Procedure Editor)
          Table Name:       (set in the "New PL/SQL Object" dialog)

       Return code retVar defination:
       0: success.
       1: no input operator id;
       2: no input partno or partno is not correct or partno is invalid;
       3: supplier is null;
       4: supplier and partno mismatch;
       5: supplier master data haven't been maintained;
       6: cannot GR due to this part requires warrenty management but no shelf life info input;
       7: no serial no.
       8: duplicated SN.
       9: part requires serial no management but gr qty <> 1
       1~9 are exception in gr_check function
       10: general exception that haven't been caught
       11: label split failed
       12: Exception in update inventory/packages/transactions table

    ******************************************************************************/

    v_procedure      VARCHAR2 (30) := 'GR_Scanning';

    v_ret_split      VARCHAR2 (2) := 0;
    v_partno         VARCHAR2 (30);
    v_qty            NUMBER;
    v_supplier       VARCHAR2 (30);
    v_dn             VARCHAR2 (30);
    v_sn             VARCHAR2 (30);
    v_bn             VARCHAR2 (100);
    v_md             VARCHAR2 (8);
    v_dd             VARCHAR2 (8);

    v_ret_gr_check   VARCHAR2 (2) := 0;
    v_valid_day      NUMBER;

    v_ret_gr         VARCHAR2 (2) := 0;
BEGIN
    retVar := 10;                -- general exception that haven't been caught
    logger (
        'INFO',
           v_procedure
        || ' started at '
        || TO_CHAR (SYSDATE, 'yyyy-mm-dd hh24:mi:ss'),
        v_procedure,
        'PSQM');

    INSERT INTO z_scanning_log (sys_timestamp,
                                received_label_content,
                                userid,
                                hostname,
                                ip,
                                loc_id)
         VALUES (SYSDATE,
                 p_label,
                 p_user,
                 p_hostname,
                 p_ip,
                 p_loc_id);

    COMMIT;

    -- step1. split the label content, get partno/qty/supplier... info

    v_ret_split :=
        SPLIT_LABEL_CONTENT_NEW (p_label,
                                 v_partno,
                                 v_qty,
                                 v_supplier,
                                 v_dn,
                                 v_sn,
                                 v_bn,
                                 v_md,
                                 v_dd);

    IF v_ret_split <> 0
    THEN
        retVar := 11;
        logger ('ERROR',
                'Label Content split failed.',
                v_procedure,
                p_user);

        RETURN;
    END IF;

    -- step2. check if the label content can be send to GR process
    -- first calculate the due_date if possible.
    IF     (v_dd IS NULL OR v_dd = '')
       AND v_md IS NOT NULL
       AND v_partno IS NOT NULL
    THEN
        SELECT valid_day
          INTO v_valid_day
          FROM parts
         WHERE partno = v_partno;

        logger (
            'INFO',
               'Start calculating due date using partno:'
            || v_partno
            || ', manufacturing date:'
            || v_md
            || ' and valid_day: '
            || v_valid_day,
            v_procedure,
            p_user);

        v_dd :=
            TO_CHAR (TO_DATE (v_md, 'YYYYMMDD') + v_valid_day, 'YYYYMMDD');

        logger ('INFO',
                'Calculate successfully, the due_date is:' || v_dd,
                v_procedure,
                p_user);
    END IF;

    v_ret_gr_check :=
        gr_check_new (p_user,
                      v_partno,
                      v_qty,
                      v_supplier,
                      v_dd,
                      v_sn);

    logger ('INFO',
            'v_ret_gr_check:' || v_ret_gr_check,
            v_procedure,
            p_user);

    IF v_ret_gr_check <> 0
    THEN
        retVar := v_ret_gr_check;
        RETURN;
    END IF;

    INSERT INTO scanned_goods (serial_no,
                               batch_no,
                               partno,
                               qty,
                               supplier,
                               disp_note,
                               receiving_loc,
                               manufacturing_date,
                               due_date,
                               sys_timestamp,
                               userid)
         VALUES (v_sn,
                 v_bn,
                 v_partno,
                 v_qty,
                 v_supplier,
                 v_dn,
                 p_loc_id,
                 v_md,
                 v_dd,
                 SYSDATE,
                 p_user);

    COMMIT;

    --start the GR process.
    --first check other parameter is valid: serial no/qty/due date.
    IF v_qty IS NOT NULL AND v_qty <> 0 AND p_loc_id IS NOT NULL
    THEN
        --GR process
        v_ret_gr :=
            GOODS_RECEIPTION_NEW (P_LOC_ID     => P_LOC_ID,
                                  P_PARTNO     => V_PARTNO,
                                  P_QTY        => V_QTY,
                                  P_SUPPLIER   => V_SUPPLIER,
                                  P_DN         => V_DN,
                                  P_SN         => V_SN,
                                  p_bn         => v_bn,
                                  P_MD         => V_MD,
                                  P_DD         => V_DD,
                                  P_USER       => P_USER);

        IF v_ret_gr <> 0
        THEN
            retVar := 12;
            logger ('ERROR',
                    'Error in Goods_receiption.',
                    v_procedure,
                    p_user);
        END IF;

        UPDATE scanned_goods
           SET gr_result = 'Y'
         WHERE serial_no = v_sn AND reversed <> 'Y';

        retVar := 0;
        COMMIT;
    END IF;
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
            || v_procedure,
            v_procedure,
            'PSQM');           -- Consider logging the error and then re-raise
        RAISE;
END GR_Scanning_new;
/