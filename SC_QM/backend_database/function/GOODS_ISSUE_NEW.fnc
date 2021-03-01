CREATE OR REPLACE FUNCTION PSQM.goods_issue_new (p_sn     IN VARCHAR2,
                                                 p_qty    IN NUMBER,
                                                 p_user   IN VARCHAR2)
    RETURN NUMBER
IS
    retVar                     NUMBER;
    /******************************************************************************
       NAME:       goods_issue
       PURPOSE:    using this function to update inventory/packages/packages_del/transactions tables when doing GI

       REVISIONS:
       Ver        Date        Author           Description
       ---------  ----------  ---------------  ------------------------------------
       1.0        4/29/2020   CYANG44       1. Created this function.

       NOTES:

       Automatically available Auto Replace Keywords:
          Object Name:     goods_issue
          Sysdate:         4/29/2020
          Date and Time:   4/29/2020, 8:52:33 AM, and 4/29/2020 8:52:33 AM
          Username:        CYANG44 (set in TOAD Options, Procedure Editor)
          Table Name:       (set in the "New PL/SQL Object" dialog)

    ******************************************************************************/
    v_procedure                VARCHAR2 (30) := 'goods_issue';
    v_partno                   VARCHAR2 (30);
    v_issue_qty                NUMBER := p_qty;
    v_qty                      NUMBER := 0;
    v_supplier                 VARCHAR2 (30);
    v_from_loc                 VARCHAR2 (30);
    v_remaining_qty            NUMBER;
    v_dn                       VARCHAR2 (30);
    v_bn                       VARCHAR2 (100);
    v_pkg                      NUMBER;
    v_ret_insert_transaction   NUMBER;
BEGIN
    retVar := 0;
    logger ('INFO',
            'Goods issue starts!' || p_sn || p_qty,
            v_procedure,
            p_user);

    SELECT package_id,
           partno,
           supplier_id,
           qty,
           dn,
           batch_no
      INTO v_pkg,
           v_partno,
           v_supplier,
           v_qty,
           v_dn,
           v_bn
      FROM packages
     WHERE serial_no = p_sn;

    IF v_qty = 0
    THEN
        logger ('ERROR',
                'Cannot find this package.',
                v_procedure,
                p_user);
        retVar := 1;
        RETURN retVar;
    END IF;

    SELECT loc_id
      INTO v_from_loc
      FROM inventory
     WHERE serial_no = p_sn AND qty = v_qty;

    IF v_from_loc IS NULL
    THEN
        logger ('ERROR',
                'Package and inventory mismatch.',
                v_procedure,
                p_user);
        retVar := 2;
        RETURN retVar;
    END IF;

    --start the GI process.
    IF v_qty = v_issue_qty
    THEN
        --scenario 1. issue the whole package.
        DELETE FROM inventory
              WHERE     serial_no = p_sn
                    AND qty = v_issue_qty
                    AND inv_type = 'UU';

        INSERT INTO packages_del (package_id,
                                  partno,
                                  supplier_id,
                                  serial_no,
                                  prod_date,
                                  valid_day,
                                  due_date,
                                  dn,
                                  parent_sn,
                                  inv_type,
                                  batch_no)
            SELECT package_id,
                   partno,
                   supplier_id,
                   serial_no,
                   prod_date,
                   valid_day,
                   due_date,
                   dn,
                   parent_sn,
                   inv_type,
                   batch_no
              FROM packages
             WHERE serial_no = p_sn AND qty = v_issue_qty AND inv_type = 'UU';

        DELETE FROM packages
              WHERE     serial_no = p_sn
                    AND qty = v_issue_qty
                    AND inv_type = 'UU';

        COMMIT;
    ELSIF v_qty > v_issue_qty
    THEN
        --scenario 2. issue part of the package, need to update the inventory and package qty.
        v_remaining_qty := v_qty - v_issue_qty;

        UPDATE inventory
           SET qty = v_remaining_qty
         WHERE serial_no = p_sn AND qty = v_qty AND inv_type = 'UU';

        UPDATE packages
           SET qty = v_remaining_qty
         WHERE serial_no = p_sn AND qty = v_qty AND inv_type = 'UU';

        COMMIT;
    ELSE
        logger ('ERROR',
                'Error in issue qty. check again.',
                v_procedure,
                p_user);
        retVar := 3;
        RETURN retVar;
    END IF;

    -- if no error, update into the transactions table
    v_ret_insert_transaction :=
        INSERT_TRANSACTION_NEW (P_PKG        => v_pkg,
                                P_PARTNO     => v_partno,
                                P_QTY        => v_issue_qty,
                                P_SUPPLIER   => v_supplier,
                                P_MVTP       => '601',
                                P_FROM_LOC   => v_from_loc,
                                P_USERID     => P_USER,
                                P_DN         => v_dn,
                                P_SN         => p_sn,
                                P_BN         => v_bn);

    IF v_ret_insert_transaction <> 0
    THEN
        ROLLBACK;
        logger ('ERROR',
                'Error in update transaction table.',
                v_procedure,
                p_user);
        retVar := 4;
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
END goods_issue_new;
/