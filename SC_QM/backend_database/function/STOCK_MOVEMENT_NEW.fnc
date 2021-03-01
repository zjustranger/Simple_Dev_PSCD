CREATE OR REPLACE FUNCTION PSQM.stock_movement_new (p_sn         IN VARCHAR2,
                                                    p_qty        IN NUMBER,
                                                    p_from_loc   IN VARCHAR2,
                                                    p_to_loc     IN VARCHAR2,
                                                    p_user       IN VARCHAR2)
    RETURN NUMBER
IS
    tmpVar              NUMBER;
    /******************************************************************************
       NAME:       stock_movement
       PURPOSE:    use this function to do in_plant stock movement
       process:    1.update the inventory information
                   2.update the packages information
                   3.insert the transaction history.
       algorithm:  need to seperate into 2 business situation, one is whole package move, the other is split and move. more detail see comments in procedure.

       REVISIONS:
       Ver        Date        Author           Description
       ---------  ----------  ---------------  ------------------------------------
       1.0        4/22/2020   CYANG44       1. Created this function.
       2.0        5/26/2020   CYANG44       2. update this function for batch no.

       NOTES: Exit code defination
       0: success
       1: input parameter is not complete
       2: cannot move due to inventory qty is not enough
       3: cannot move from same location to same location
       4: Error in whole package movement
       5: Error in split movement
       6: Exception, move qty greater than current package

       Automatically available Auto Replace Keywords:
          Object Name:     stock_movement
          Sysdate:         4/22/2020
          Date and Time:   4/22/2020, 10:10:54 AM, and 4/22/2020 10:10:54 AM
          Username:        CYANG44 (set in TOAD Options, Procedure Editor)
          Table Name:       (set in the "New PL/SQL Object" dialog)

    ******************************************************************************/
    v_procedure         VARCHAR2 (30) := 'stock_movement';
    v_current_qty       NUMBER;
    v_move_qty          NUMBER;
    v_remaining_qty     NUMBER;
    v_pkg_id            NUMBER;
    v_partno            VARCHAR2 (30);
    v_supplier          VARCHAR2 (30);
    v_dn                VARCHAR2 (30);
    v_ret_transaction   NUMBER := 0;
    v_new_sn            VARCHAR2 (30);
    v_inv_type          CHAR (2);
    v_bn                VARCHAR2 (100);
    v_pd                VARCHAR2 (8);
    v_valid_day         INTEGER;
    v_dd                VARCHAR2 (8);
    v_parent_sn         VARCHAR2 (30);
    v_inv_qty           NUMBER;
BEGIN
    tmpVar := 0;

    IF    p_sn IS NULL
       OR p_qty IS NULL
       OR p_qty = 0
       OR p_from_loc IS NULL
       OR p_to_loc IS NULL
       OR p_user IS NULL
    THEN
        logger ('ERROR',
                'input parameter is not complete!',
                v_procedure,
                p_user);
        tmpVar := 1;
        RETURN tmpVar;
    END IF;

    SELECT package_id,
           partno,
           supplier_id,
           prod_date,
           valid_day,
           due_date,
           dn,
           batch_no,
           inv_type,
           qty
      INTO v_pkg_id,
           v_partno,
           v_supplier,
           v_pd,
           v_valid_day,
           v_dd,
           v_dn,
           v_bn,
           v_inv_type,
           v_current_qty
      FROM packages
     WHERE serial_no = p_sn;

    v_move_qty := p_qty;
    v_remaining_qty := v_current_qty - v_move_qty;

    SELECT qty
      INTO v_inv_qty
      FROM inventory
     WHERE     loc_id = p_from_loc
           AND package_id = v_pkg_id
           AND partno = v_partno
           AND inv_type = v_inv_type
           AND serial_no = p_sn;

    IF v_inv_qty < v_move_qty
    THEN
        logger ('ERROR',
                'Move more qty than inventory',
                v_procedure,
                p_user);
        tmpVar := 2;
        RETURN tmpVar;
    END IF;

    IF p_from_loc = p_to_loc
    THEN
        logger ('ERROR',
                'Cannot move due to same location.',
                v_procedure,
                p_user);
        tmpVar := 3;
        RETURN tmpVar;
    END IF;

    IF v_remaining_qty = 0
    THEN
        --scenario 1: move for the whole package

        --step1. update the inventory table
        UPDATE inventory
           SET loc_id = p_to_loc
         WHERE     loc_id = p_from_loc
               AND package_id = v_pkg_id
               AND partno = v_partno
               AND inv_type = v_inv_type
               AND serial_no = p_sn;

        --step2. no need to update package info, skip this step

        --step3. insert the transaction history.
        v_ret_transaction :=
            PSQM.INSERT_TRANSACTION_NEW (P_PKG        => v_pkg_id,
                                         P_PARTNO     => v_partno,
                                         P_QTY        => v_move_qty,
                                         P_SUPPLIER   => v_supplier,
                                         P_MVTP       => '311',
                                         P_FROM_LOC   => p_from_loc,
                                         P_TO_LOC     => p_to_loc,
                                         P_USERID     => p_user,
                                         P_DN         => v_dn,
                                         P_SN         => p_sn,
                                         P_BN         => v_bn);

        IF v_ret_transaction <> 0
        THEN
            ROLLBACK;
            logger ('ERROR',
                    'ERROR in whole package movement.',
                    v_procedure,
                    p_user);
            tmpVar := 4;
            RETURN tmpVar;
        END IF;
    ELSIF v_remaining_qty > 0
    THEN
        -- scenario 2: split package and movement, current logic is always generate new sn for child package
        -- generate new sn for child package
        v_new_sn := REQUEST_FOR_NEW_CHILD_SN (p_sn => p_sn, p_user => p_user);

        IF v_new_sn IS NULL
        THEN
            logger ('ERROR',
                    'Cannot generate new child SN.',
                    v_procedure,
                    p_user);
            tmpVar := 5;
            RETURN tmpVar;
        END IF;

        -- step 1: update the inventory table.
        INSERT INTO inventory (loc_id,
                               package_id,
                               partno,
                               inv_type,
                               qty,
                               serial_no)
             VALUES (p_to_loc,
                     v_pkg_id,
                     v_partno,
                     v_inv_type,
                     v_move_qty,
                     v_new_sn);

        UPDATE inventory
           SET qty = qty - v_move_qty
         WHERE     loc_id = p_from_loc
               AND package_id = v_pkg_id
               AND partno = v_partno
               AND inv_type = v_inv_type
               AND serial_no = p_sn;

        -- step 2: update Packages table.
        UPDATE packages
           SET qty = v_remaining_qty
         WHERE package_id = v_pkg_id AND serial_no = p_sn;

        -- insert new package
        INSERT INTO packages (package_id,
                              partno,
                              supplier_id,
                              serial_no,
                              prod_date,
                              valid_day,
                              due_date,
                              dn,
                              parent_sn,
                              inv_type,
                              batch_no,
                              qty)
             VALUES (v_pkg_id,
                     v_partno,
                     v_supplier,
                     v_new_sn,
                     v_pd,
                     v_valid_day,
                     v_dd,
                     v_dn,
                     p_sn,
                     v_inv_type,
                     v_bn,
                     v_move_qty);

        -- step 3: update the transactions table
        v_ret_transaction :=
            PSQM.INSERT_TRANSACTION_NEW (P_PKG        => v_pkg_id,
                                         P_PARTNO     => v_partno,
                                         P_QTY        => v_move_qty,
                                         P_SUPPLIER   => v_supplier,
                                         P_MVTP       => '311',
                                         P_FROM_LOC   => p_from_loc,
                                         P_USERID     => p_user,
                                         P_DN         => v_dn,
                                         P_SN         => p_sn,
                                         P_BN         => v_bn);

        IF v_ret_transaction <> 0
        THEN
            ROLLBACK;
            logger ('ERROR',
                    'ERROR in split package movement.',
                    v_procedure,
                    p_user);
            tmpVar := 5;
            RETURN tmpVar;
        END IF;

        v_ret_transaction :=
            PSQM.INSERT_TRANSACTION_NEW (P_PKG        => v_pkg_id,
                                         P_PARTNO     => v_partno,
                                         P_QTY        => v_move_qty,
                                         P_SUPPLIER   => v_supplier,
                                         P_MVTP       => '311',
                                         P_TO_LOC     => p_to_loc,
                                         P_USERID     => p_user,
                                         P_DN         => v_dn,
                                         P_SN         => v_new_sn,
                                         P_BN         => v_bn);

        IF v_ret_transaction <> 0
        THEN
            ROLLBACK;
            logger ('ERROR',
                    'ERROR in split package movement.',
                    v_procedure,
                    p_user);
            tmpVar := 5;
            RETURN tmpVar;
        END IF;

        UPDATE downsize_history dh
           SET transaction_seq =
                   (SELECT ts.seq
                      FROM transactions ts
                     WHERE     dh.CHILD_SN = ts.serial_no
                           AND ts.movement_type = '311'
                           AND ts.sys_timestamp - dh.sys_timestamp <=
                               2 / (24 * 3600))
         WHERE child_sn = v_new_sn;

        COMMIT;
    ELSE
        logger ('ERROR',
                'move qty greater than package qty.',
                v_procedure,
                p_user);
        tmpVar := 6;
        RETURN tmpVar;
    END IF;

    RETURN tmpVar;
EXCEPTION
    WHEN NO_DATA_FOUND
    THEN
        logger ('ERROR',
                'NO_DATA_FOUND Exception.',
                v_procedure,
                p_user);
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
            p_user);           -- Consider logging the error and then re-raise
        RAISE;
END stock_movement_new;
/