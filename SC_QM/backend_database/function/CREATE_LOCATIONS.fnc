CREATE OR REPLACE FUNCTION PSQM.create_locations (p_loc         IN VARCHAR2,
                                             p_loc_descr   IN VARCHAR2,
                                             p_loc_type    IN VARCHAR2,
                                             p_user        IN VARCHAR2)
    RETURN NUMBER
IS
    retVar        NUMBER;
    /******************************************************************************
       NAME:       create_locations
       PURPOSE:    use this function to do some check and create locations.

       REVISIONS:
       Ver        Date        Author           Description
       ---------  ----------  ---------------  ------------------------------------
       1.0        5/19/2020   CYANG44       1. Created this function.

       NOTES:

       Automatically available Auto Replace Keywords:
          Object Name:     create_locations
          Sysdate:         5/19/2020
          Date and Time:   5/19/2020, 12:26:54 PM, and 5/19/2020 12:26:54 PM
          Username:        CYANG44 (set in TOAD Options, Procedure Editor)
          Table Name:       (set in the "New PL/SQL Object" dialog)

       Return Code defination:
       0: success
       1: general exception not been caught
       2: location already exists

    ******************************************************************************/
    v_procedure   VARCHAR2 (30) := 'create_locations';
    v_cnt         NUMBER;
    v_loc         VARCHAR2 (30);
BEGIN
    retVar := 1;
    logger ('INFO',
            'create location starts for loc: ' || p_loc,
            v_procedure,
            p_user);

    --step 1. check if the location already exists.
    SELECT COUNT (1)
      INTO v_cnt
      FROM locations
     WHERE loc_id = p_loc;

    IF v_cnt <> 0
    THEN
        logger ('ERROR',
                'location already exists!',
                v_procedure,
                p_user);
        retVar := 2;
        RETURN retVar;
    END IF;

    INSERT INTO locations (loc_id, loc_type, loc_descr)
         VALUES (p_loc, p_loc_type, p_loc_descr);

    COMMIT;

    retVar := 0;
    RETURN retVar;
EXCEPTION
    WHEN OTHERS
    THEN
        -- Consider logging the error and then re-raise
        RAISE;
END create_locations;
/