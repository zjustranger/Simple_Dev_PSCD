CREATE OR REPLACE FUNCTION PSQM.get_new_generated_child_sn (
    p_user   IN VARCHAR2)
    RETURN VARCHAR2
IS
    child_sn      VARCHAR2 (30);
    /******************************************************************************
       NAME:       get_new_generated_child_sn
       PURPOSE:

       REVISIONS:
       Ver        Date        Author           Description
       ---------  ----------  ---------------  ------------------------------------
       1.0        4/27/2020   CYANG44       1. Created this function.

       NOTES:

       Automatically available Auto Replace Keywords:
          Object Name:     get_new_generated_child_sn
          Sysdate:         4/27/2020
          Date and Time:   4/27/2020, 1:06:53 PM, and 4/27/2020 1:06:53 PM
          Username:        CYANG44 (set in TOAD Options, Procedure Editor)
          Table Name:       (set in the "New PL/SQL Object" dialog)

    ******************************************************************************/
    v_procedure   VARCHAR2 (30) := 'get_new_generated_sn';
BEGIN
    child_sn := NULL;

    SELECT child_sn
      INTO child_sn
      FROM downsize_history
     WHERE     userid = p_user
           AND sys_timestamp > SYSDATE - 10 / (24 * 60 * 60)
           AND transaction_seq = (SELECT MAX (transaction_seq)
                                    FROM downsize_history
                                   WHERE userid = p_user);

    logger ('INFO',
            'return new generated child sn: ' || child_sn,
            v_procedure,
            p_user);

    RETURN child_sn;
EXCEPTION
    WHEN NO_DATA_FOUND
    THEN
        NULL;
    WHEN OTHERS
    THEN
        -- Consider logging the error and then re-raise
        RAISE;
END get_new_generated_child_sn;
/