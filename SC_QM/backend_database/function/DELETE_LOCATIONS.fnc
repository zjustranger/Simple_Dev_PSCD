CREATE OR REPLACE FUNCTION PSQM.delete_locations (p_loc         IN VARCHAR2,
                                             p_loc_descr   IN VARCHAR2,
                                             p_loc_type    IN VARCHAR2,
                                             p_user        IN VARCHAR2)
    RETURN NUMBER
IS
    retVar        NUMBER;
    /******************************************************************************
       NAME:       delete_locations
       PURPOSE:

       REVISIONS:
       Ver        Date        Author           Description
       ---------  ----------  ---------------  ------------------------------------
       1.0        5/19/2020   CYANG44       1. Created this function.

       NOTES:

       Automatically available Auto Replace Keywords:
          Object Name:     delete_locations
          Sysdate:         5/19/2020
          Date and Time:   5/19/2020, 12:53:00 PM, and 5/19/2020 12:53:00 PM
          Username:        CYANG44 (set in TOAD Options, Procedure Editor)
          Table Name:       (set in the "New PL/SQL Object" dialog)

       Return code defination:
       0: success
       1: general exception that not been caught
       2: location exists in location structure, cannot delete directly
       3: location still has inventory, cannot delete.

    ******************************************************************************/
    v_procedure   VARCHAR2 (30) := 'delete_locations';
    v_cnt         NUMBER;
    v_cnt1        NUMBER;
    v_cnt2        NUMBER;
    v_loc         VARCHAR2 (30);
BEGIN
    retVar := 1;
    logger ('INFO',
            'delete location starts for loc: ' || p_loc,
            v_procedure,
            p_user);

    --step 1. check if the location exists in location structure.
    SELECT COUNT (1)
      INTO v_cnt1
      FROM location_structure
     WHERE loc_id = p_loc;

    SELECT COUNT (1)
      INTO v_cnt2
      FROM location_structure
     WHERE subloc_id = p_loc;

    v_cnt := v_cnt1 + v_cnt2;

    IF v_cnt <> 0
    THEN
        retVar := 2;
        RETURN retVar;
    END IF;

    -- step 2. check if there are parts in the location
    SELECT COUNT (1)
      INTO v_cnt
      FROM inventory
     WHERE loc_id = p_loc;

    IF v_cnt <> 0
    THEN
        retVar := 3;
        RETURN retVar;
    END IF;

    -- step 3. delete location
    DELETE FROM locations
          WHERE loc_id = p_loc;

    COMMIT;

    logger ('INFO',
            'location has been deleted successfully! location: ' || p_loc,
            v_procedure,
            p_user);
    retVar := 0;
    RETURN retVar;
EXCEPTION
    WHEN NO_DATA_FOUND
    THEN
        NULL;
    WHEN OTHERS
    THEN
        -- Consider logging the error and then re-raise
        RAISE;
END delete_locations;
/