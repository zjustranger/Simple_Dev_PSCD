CREATE OR REPLACE FUNCTION PSQM.bind_locations (p_loc      IN VARCHAR2,
                                           p_subloc   IN VARCHAR2,
                                           p_user     IN VARCHAR2)
    RETURN VARCHAR2
IS
    retloc        VARCHAR2 (30);
    /******************************************************************************
       NAME:       bind_locations
       PURPOSE:    use this function to add location_structure

       REVISIONS:
       Ver        Date        Author           Description
       ---------  ----------  ---------------  ------------------------------------
       1.0        5/19/2020   CYANG44       1. Created this function.

       NOTES:

       Automatically available Auto Replace Keywords:
          Object Name:     bind_locations
          Sysdate:         5/19/2020
          Date and Time:   5/19/2020, 1:24:34 PM, and 5/19/2020 1:24:34 PM
          Username:        CYANG44 (set in TOAD Options, Procedure Editor)
          Table Name:       (set in the "New PL/SQL Object" dialog)

    ******************************************************************************/
    v_procedure   VARCHAR2 (30) := 'bind_locations';
    v_cnt         NUMBER;
BEGIN
    retloc := NULL;

    logger ('INFO',
            'location structure adding starts: ' || p_loc || p_subloc,
            v_procedure,
            p_user);

    --step 1. check if subloc already exist in another warehouse.
    SELECT COUNT (1)
      INTO v_cnt
      FROM location_structure
     WHERE subloc_id = p_subloc;

    IF v_cnt <> 0
    THEN
        SELECT loc_id
          INTO retloc
          FROM location_structure
         WHERE subloc_id = p_subloc;
    END IF;

    IF retloc IS NOT NULL
    THEN
        RETURN retloc;
    END IF;

    --step 2. add location structure and return 0
    INSERT INTO location_structure (loc_id,
                                    loc_type,
                                    subloc_id,
                                    subloc_type)
         VALUES (p_loc,
                 (SELECT loc_type
                    FROM locations
                   WHERE loc_id = p_loc),
                 p_subloc,
                 (SELECT loc_type
                    FROM locations
                   WHERE loc_id = p_subloc));

    COMMIT;
    retloc := '0';

    RETURN retloc;
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
            || v_procedure
            || ', the input parameter is:'
            || p_loc
            || '/'
            || p_subloc
            || '/'
            || p_user,
            v_procedure,
            'PSQM');
        -- Consider logging the error and then re-raise
        RAISE;
END bind_locations;
/