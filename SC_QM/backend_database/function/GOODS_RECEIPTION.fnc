CREATE OR REPLACE FUNCTION PSQM.goods_receiption (p_loc_id     IN VARCHAR2,
                                                  p_partno     IN VARCHAR2,
                                                  p_qty           NUMBER,
                                                  p_supplier   IN VARCHAR2,
                                                  p_dn         IN VARCHAR2,
                                                  p_sn         IN VARCHAR2,
                                                  p_md         IN VARCHAR2,
                                                  p_dd         IN VARCHAR2,
                                                  p_user       IN VARCHAR2)
    RETURN NUMBER
IS
    retVar                     NUMBER;
    /******************************************************************************
       NAME:       goods_receiption
       PURPOSE:    GR process. insert into inventory, packages

       REVISIONS:
       Ver        Date        Author           Description
       ---------  ----------  ---------------  ------------------------------------
       1.0        4/21/2020   CYANG44       1. Created this function.

       NOTES:

       Automatically available Auto Replace Keywords:
          Object Name:     goods_receiption
          Sysdate:         4/21/2020
          Date and Time:   4/21/2020, 9:05:41 AM, and 4/21/2020 9:05:41 AM
          Username:        CYANG44 (set in TOAD Options, Procedure Editor)
          Table Name:       (set in the "New PL/SQL Object" dialog)

    ******************************************************************************/
    v_procedure                VARCHAR2 (30) := 'GOODS_RECEIPTION';
    v_seq_package_id           NUMBER;
    v_ret_insert_transaction   VARCHAR2 (2) := 0;
BEGIN
    retVar := 0;
    logger (
        'INFO',
           'Start GR Process.'
        || p_loc_id
        || '/'
        || p_partno
        || '/'
        || p_qty
        || '/'
        || p_supplier
        || '/'
        || p_dn
        || '/'
        || p_sn
        || '/'
        || p_md
        || '/'
        || p_dd
        || '/'
        || p_user,
        v_procedure,
        p_user);

    -- insert into packages table.
    SELECT package_seq.NEXTVAL INTO v_seq_package_id FROM DUAL;

    INSERT INTO packages (package_id,
                          partno,
                          supplier_id,
                          serial_no,
                          prod_date,
                          due_date,
                          dn,
                          qty,
                          inv_type)
         VALUES (v_seq_package_id,
                 p_partno,
                 p_supplier,
                 p_sn,
                 p_md,
                 p_dd,
                 p_dn,
                 p_qty,
                 'UU');

    -- insert into inventory table.
    INSERT INTO inventory (loc_id,
                           package_id,
                           partno,
                           inv_type,
                           qty,
                           serial_no)
         VALUES (p_loc_id,
                 v_seq_package_id,
                 p_partno,
                 'UU',
                 p_qty,
                 p_sn);

    --update the transactions table.
    v_ret_insert_transaction :=
        INSERT_TRANSACTION (P_PKG        => v_seq_package_id,
                            P_PARTNO     => p_partno,
                            P_QTY        => P_QTY,
                            P_SUPPLIER   => P_SUPPLIER,
                            P_MVTP       => '101',
                            P_TO_LOC     => p_loc_id,
                            P_USERID     => P_USER,
                            P_DN         => p_dn,
                            P_SN         => p_sn);

    IF v_ret_insert_transaction <> 0
    THEN
        ROLLBACK;
        logger ('ERROR',
                'Error in update transaction table.',
                v_procedure,
                p_user);
        retVar := 1;
        RETURN retVar;
    END IF;

    RETURN retVar;
EXCEPTION
    WHEN NO_DATA_FOUND
    THEN
        NULL;
    WHEN OTHERS
    THEN
        -- Consider logging the error and then re-raise
        RAISE;
END goods_receiption;
/