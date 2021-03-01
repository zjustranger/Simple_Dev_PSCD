CREATE OR REPLACE FUNCTION PSQM.unbind_locations (p_loc      IN VARCHAR2,
                                             p_subloc   IN VARCHAR2,
                                             p_user     IN VARCHAR2)
    RETURN NUMBER
IS
    retVar        NUMBER;
    /******************************************************************************
       NAME:       unbind_locations
       PURPOSE:

       REVISIONS:
       Ver        Date        Author           Description
       ---------  ----------  ---------------  ------------------------------------
       1.0        5/19/2020   CYANG44       1. Created this function.

       NOTES:

       Automatically available Auto Replace Keywords:
          Object Name:     unbind_locations
          Sysdate:         5/19/2020
          Date and Time:   5/19/2020, 2:02:01 PM, and 5/19/2020 2:02:01 PM
          Username:        CYANG44 (set in TOAD Options, Procedure Editor)
          Table Name:       (set in the "New PL/SQL Object" dialog)

    ******************************************************************************/
    v_procedure   VARCHAR2 (30) := 'unbind_locations';
    v_cnt         NUMBER;
BEGIN
    retVar := 1;
    logger ('INFO',
            'unbind locations starts: ' || p_loc || p_subloc,
            v_procedure,
            p_user);

    --step 1. check if there are parts on the location.
    SELECT COUNT (1)
      INTO v_cnt
      FROM inventory
     WHERE loc_id = p_subloc;

    IF v_cnt <> 0
    THEN
        logger ('ERROR',
                'location has inventory, cannot unlink.',
                v_procedure,
                p_user);
        retVar := 2;
        RETURN retVar;
    END IF;

    DELETE FROM location_structure
          WHERE loc_id = p_loc AND subloc_id = p_subloc;

    COMMIT;


    retVar := 0;
    RETURN retVar;
EXCEPTION
    WHEN OTHERS
    THEN
        -- Consider logging the error and then re-raise
        RAISE;
END unbind_locations;
/