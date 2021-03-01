CREATE OR REPLACE FUNCTION PSQM.update_locations (p_loc         IN VARCHAR2,
                                             p_loc_descr   IN VARCHAR2,
                                             p_loc_type    IN VARCHAR2,
                                             p_user        IN VARCHAR2)
    RETURN NUMBER
IS
    retVar        NUMBER;
    /******************************************************************************
       NAME:       update_locations
       PURPOSE:    use this funtion to do some check and update location

       REVISIONS:
       Ver        Date        Author           Description
       ---------  ----------  ---------------  ------------------------------------
       1.0        5/19/2020   CYANG44       1. Created this function.

       NOTES:

       Automatically available Auto Replace Keywords:
          Object Name:     update_locations
          Sysdate:         5/19/2020
          Date and Time:   5/19/2020, 9:55:30 AM, and 5/19/2020 9:55:30 AM
          Username:        CYANG44 (set in TOAD Options, Procedure Editor)
          Table Name:       (set in the "New PL/SQL Object" dialog)

       Return Code defination:
       0: success
       1: general exception that not been caught
       2: the location already exists in location_structure, we can only update its description, cannot update location type directly

    ******************************************************************************/
    v_procedure   VARCHAR2 (30) := 'update_locations';
    v_cnt         NUMBER;
    v_cnt1        NUMBER;
    v_cnt2        NUMBER;
    v_loc_type    VARCHAR2 (30);
BEGIN
    retVar := 1;
    logger ('INFO',
            'update_locations start for loc: ' || p_loc,
            v_procedure,
            p_user);

    --step 1. find the original loc_type, compare if this is loc_type change.
    SELECT loc_type
      INTO v_loc_type
      FROM locations
     WHERE loc_id = p_loc;

    IF p_loc_type <> v_loc_type
    THEN
        --find if the location exists in loc_structure.
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
    END IF;

    -- step 2. update locations.
    logger (
        'INFO',
        'update locations: ' || p_loc || ',' || p_loc_type || p_loc_descr,
        v_procedure,
        p_user);

    UPDATE locations
       SET loc_type = p_loc_type, loc_descr = p_loc_descr
     WHERE loc_id = p_loc;

    COMMIT;

    retVar := 0;
    RETURN retVar;
EXCEPTION
    WHEN OTHERS
    THEN
        -- Consider logging the error and then re-raise
        RAISE;
END update_locations;
/