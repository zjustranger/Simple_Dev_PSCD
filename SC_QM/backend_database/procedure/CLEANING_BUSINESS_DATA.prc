CREATE OR REPLACE PROCEDURE PSQM.Cleaning_Business_Data
IS
    tmpVar        NUMBER;
    /******************************************************************************
       NAME:       Cleaning_Business_Data
       PURPOSE:    Create this procedure to cleanning all business transaction data.

       REVISIONS:
       Ver        Date        Author           Description
       ---------  ----------  ---------------  ------------------------------------
       1.0        4/22/2020   CYANG44       1. Created this procedure.

       NOTES:

       Automatically available Auto Replace Keywords:
          Object Name:     Cleaning_Business_Data
          Sysdate:         4/22/2020
          Date and Time:   4/22/2020, 12:35:09 PM, and 4/22/2020 12:35:09 PM
          Username:        CYANG44 (set in TOAD Options, Procedure Editor)
          Table Name:       (set in the "New PL/SQL Object" dialog)

    ******************************************************************************/

    v_procedure   VARCHAR (30) := 'cleaning_business_data';
BEGIN
    tmpVar := 0;

    logger ('INFO',
            'Cleaning Business Data Start!',
            v_procedure,
            'PSQM');

    DELETE FROM downsize_history;

    DELETE FROM inventory;

    DELETE FROM packages;

    DELETE FROM packages_del;

    DELETE FROM transactions;

    DELETE FROM z_scanning_log;

    DELETE FROM scanned_goods;

    COMMIT;

    logger ('INFO',
            'Cleaning Business Data Finished!',
            v_procedure,
            'PSQM');
EXCEPTION
    WHEN NO_DATA_FOUND
    THEN
        NULL;
    WHEN OTHERS
    THEN
        ROLLBACK;
        logger (
            'ERROR',
            'Error in cleaning business data, debug the procedure to find reason.',
            v_procedure,
            'PSQM');
        -- Consider logging the error and then re-raise
        RAISE;
END Cleaning_Business_Data;
/