CREATE OR REPLACE PROCEDURE PSQM.feedback_best_package (
    p_sn          IN     VARCHAR2,
    match_code       OUT NUMBER,
    chem_flag_x      OUT VARCHAR2,
    best_sn          OUT VARCHAR2,
    out_loc          OUT VARCHAR2,
    out_qty          OUT NUMBER,
    out_dd           OUT VARCHAR2)
IS
    tmpVar        NUMBER;
    /******************************************************************************
       NAME:       feedback_best_package
       PURPOSE:    input SN (which is from the current scanning package), output if the package is the best package to be issued.

       REVISIONS:
       Ver        Date        Author           Description
       ---------  ----------  ---------------  ------------------------------------
       1.0        4/29/2020   CYANG44       1. Created this procedure.

       NOTES:

       Automatically available Auto Replace Keywords:
          Object Name:     feedback_best_package
          Sysdate:         4/29/2020
          Date and Time:   4/29/2020, 12:51:37 PM, and 4/29/2020 12:51:37 PM
          Username:        CYANG44 (set in TOAD Options, Procedure Editor)
          Table Name:       (set in the "New PL/SQL Object" dialog)

       Parameter Defination:
       p_sn: input serial number of the scanning label
       match_code: the code reprent for the checking result after calculation:
            0: this input SN is the best package to be issued.
            1: general mismatch initialization.
            2: parts without shelf life management, mismatch due to there are smaller package.
            3: parts without shelf life management, early GR packages exists
            6: parts with shelf life management, exists packages may past due earlier.
            7: parts with shelf life management, exists packages may GR earlier.
            8: parts with shelf life management, exists small packages.

       chem_flag: represent if the chemical part needs shelf life management.
       best_sn: sn of the best package to be issued.
       out_loc: the best package's location.
       out_qty: the best package's qty.
       out_dd: best packages's due date. if part needs shelf life management.

       procedure logic: get the partno from the SN. then we can check if the partno needs shelf life management.
                        check in all the warehouse locations to find the best package of this partno to be issued.
                        the decided sort sequence is due_date(with shelf life management) -> GR_Date -> Qty (small package issued first)

    ******************************************************************************/

    v_procedure   VARCHAR2 (30) := 'feedback_best_package';
    v_partno      VARCHAR2 (30);
    in_loc        VARCHAR2 (30);
    in_pkg        NUMBER;
    in_qty        NUMBER;
    out_pkg       NUMBER;
    in_dd         VARCHAR2 (8);
BEGIN
    tmpVar := 0;
    logger ('INFO',
            'Start! Trying to find the best package to be issued.',
            v_procedure,
            'PSQM');

    match_code := 1;

    --get current information of the package input.
    --get the partno, location, qty
    SELECT partno,
           loc_id,
           qty,
           package_id
      INTO v_partno,
           in_loc,
           in_qty,
           in_pkg
      FROM inventory
     WHERE serial_no = p_sn;

    --get the chemical_flag, which represents if this partno needs shelf life management.
    SELECT chem_flag
      INTO chem_flag_x
      FROM parts
     WHERE partno = v_partno;

    --get the current due date
    SELECT due_date
      INTO in_dd
      FROM packages
     WHERE serial_no = p_sn;

    IF chem_flag_x IS NULL
    THEN
        --scenario 1. parts that no need to manage shelf life
        SELECT serial_no, qty, package_id
          INTO best_sn, out_qty, out_pkg
          FROM (  SELECT *
                    FROM packages
                   WHERE partno = v_partno
                ORDER BY package_id, qty)
         WHERE ROWNUM = 1;

        SELECT loc_id
          INTO out_loc
          FROM inventory
         WHERE     serial_no = best_sn
               AND package_id = out_pkg
               AND qty = out_qty
               AND inv_type = 'UU';

        IF best_sn = p_sn
        THEN
            -- input is the best package
            match_code := 0;
        ELSIF in_pkg = out_pkg
        THEN
            -- pkg_id is the same, they are from same GR, should be different in the qty
            match_code := 2;
        ELSE
            -- pkg_id mismatch, there are packages GR earlier
            match_code := 3;
        END IF;
    ELSE
        --scenario 2. parts with shelf life management
        SELECT serial_no,
               qty,
               due_date,
               package_id
          INTO best_sn,
               out_qty,
               out_dd,
               out_pkg
          FROM (  SELECT *
                    FROM packages
                   WHERE partno = v_partno
                ORDER BY due_date, package_id, qty)
         WHERE ROWNUM = 1;

        SELECT loc_id
          INTO out_loc
          FROM inventory
         WHERE     serial_no = best_sn
               AND package_id = out_pkg
               AND qty = out_qty
               AND inv_type = 'UU';

        IF best_sn = p_sn
        THEN
            -- input is the best package
            match_code := 0;
        ELSIF in_dd <> out_dd
        THEN
            -- there are package may past due earlier
            match_code := 6;
        ELSIF in_pkg <> out_pkg
        THEN
            -- same due_date, different GR sequence, there are earlier GR packages.
            match_code := 7;
        ELSE
            --due_date, GR all matches, should be different in package size.
            match_code := 8;
        END IF;
    END IF;

    RETURN;
EXCEPTION
    WHEN OTHERS
    THEN
        -- Consider logging the error and then re-raise
        RAISE;
END feedback_best_package;
/