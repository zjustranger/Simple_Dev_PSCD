CREATE OR REPLACE FUNCTION PSQM.change_stock_status (p_sn            IN VARCHAR2,
                                                p_into_status   IN VARCHAR2,
                                                p_user          IN VARCHAR2)
    RETURN NUMBER
IS
    retVar              NUMBER;
    /******************************************************************************
       NAME:       change_stock_status
       PURPOSE:    use this function to change the stock status, for serial no parts

       REVISIONS:
       Ver        Date        Author           Description
       ---------  ----------  ---------------  ------------------------------------
       1.0        2020/5/29   CYANG44       1. Created this function.

       NOTES:

       Automatically available Auto Replace Keywords:
          Object Name:     change_stock_status
          Sysdate:         2020/5/29
          Date and Time:   2020/5/29, 13:08:12, and 2020/5/29 13:08:12
          Username:        CYANG44 (set in TOAD Options, Procedure Editor)
          Table Name:       (set in the "New PL/SQL Object" dialog)

       Return code defination:
       0: Success.
       1: p_sn in NULL
       2: into_status is not included in the pre-defined stock status.
       3: from inv_type equal to_inv_type, no need to change
       9: other exception

    ******************************************************************************/

    v_from_inv_type     VARCHAR2 (2);
    v_to_inv_type       VARCHAR2 (2);
    v_mvmt              VARCHAR2 (3);
    v_pkg               NUMBER;
    v_partno            VARCHAR2 (30);
    v_qty               NUMBER;
    v_supplier          VARCHAR2 (30);
    v_loc               VARCHAR2 (30);
    v_dn                VARCHAR2 (30);
    v_bn                VARCHAR2 (50);
    v_ret_transaction   NUMBER := 0;
    v_procedure         VARCHAR2 (30) := 'change_stock_status';
BEGIN
    retVar := 0;

    -- step 1. check input SN is not NULL
    IF p_sn IS NULL OR p_sn = ''
    THEN
        retVar := 1;
        RETURN retVar;
    END IF;

    -- step 2. translate stock status on UI to status defined in database.
    IF p_into_status = 'Õý³£'
    THEN
        v_to_inv_type := 'UU';
    ELSIF p_into_status = '´ý¼ì²é'
    THEN
        v_to_inv_type := 'QM';
    ELSIF p_into_status = '´ýÎ¬ÐÞ'
    THEN
        v_to_inv_type := 'WR';
    ELSE
        retVar := 2;
        RETURN retVar;
    END IF;

    -- step 3. get the original stock status, define the movement type need to be inserted into transactions table.
    SELECT inv_type
      INTO v_from_inv_type
      FROM packages
     WHERE serial_no = p_sn;

    IF v_from_inv_type = v_to_inv_type
    THEN
        retVar := 3;
        RETURN retVar;
    ELSE
        IF v_from_inv_type = 'UU' AND v_to_inv_type = 'QM'
        THEN
            v_mvmt := '322';
        ELSIF v_from_inv_type = 'UU' AND v_to_inv_type = 'WR'
        THEN
            v_mvmt := '341';
        ELSIF v_from_inv_type = 'QM' AND v_to_inv_type = 'UU'
        THEN
            v_mvmt := '321';
        ELSIF v_from_inv_type = 'QM' AND v_to_inv_type = 'WR'
        THEN
            v_mvmt := '331';
        ELSIF v_from_inv_type = 'WR' AND v_to_inv_type = 'UU'
        THEN
            v_mvmt := '342';
        ELSIF v_from_inv_type = 'WR' AND v_to_inv_type = 'QM'
        THEN
            v_mvmt := '332';
        ELSE
            v_mvmt := '999';
        END IF;
    END IF;

    -- step 4. update the inventory table and packages table, then insert the transaction history.
    logger (
        'INFO',
           'Start stock change for SN:'
        || p_sn
        || ', from inv_type:'
        || v_from_inv_type
        || ' to inv_type:'
        || v_to_inv_type,
        v_procedure,
        p_user);

    SELECT package_id,
           partno,
           qty,
           supplier_id,
           dn,
           batch_no
      INTO v_pkg,
           v_partno,
           v_qty,
           v_supplier,
           v_dn,
           v_bn
      FROM packages
     WHERE serial_no = p_sn;

    SELECT loc_id
      INTO v_loc
      FROM inventory
     WHERE serial_no = p_sn;

    --update inventory
    UPDATE inventory
       SET inv_type = v_to_inv_type
     WHERE serial_no = p_sn AND inv_type = v_from_inv_type;

    --update packages
    UPDATE packages
       SET inv_type = v_to_inv_type
     WHERE serial_no = p_sn AND inv_type = v_from_inv_type;

    COMMIT;

    --insert transaction
    v_ret_transaction :=
        PSQM.INSERT_TRANSACTION_NEW (P_PKG        => v_pkg,
                                     P_PARTNO     => v_partno,
                                     P_QTY        => v_qty,
                                     P_SUPPLIER   => v_supplier,
                                     P_MVTP       => v_mvmt,
                                     P_FROM_LOC   => v_loc,
                                     P_TO_LOC     => v_loc,
                                     P_USERID     => p_user,
                                     P_DN         => v_dn,
                                     P_SN         => p_sn,
                                     P_BN         => v_bn);

    IF v_ret_transaction <> 0
    THEN
        logger ('ERROR',
                'ERROR in add record for stock status change',
                v_procedure,
                p_user);
    END IF;

    RETURN retVar;
EXCEPTION
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
            p_user);
        -- Consider logging the error and then re-raise
        RAISE;
END change_stock_status;
/