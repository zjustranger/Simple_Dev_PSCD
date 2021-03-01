CREATE OR REPLACE PROCEDURE PSQM.logger (log_type   IN VARCHAR2 DEFAULT NULL,
                                         MESSAGE    IN VARCHAR2 DEFAULT NULL,
                                         pgm        IN VARCHAR2 DEFAULT NULL,
                                         userid     IN VARCHAR2 DEFAULT NULL)
IS
    tmpVar   NUMBER;
/******************************************************************************
   NAME:       logger
   PURPOSE:     Using this procedure to record all logs in the system

   REVISIONS:
   Ver        Date        Author           Description
   ---------  ----------  ---------------  ------------------------------------
   1.0        4/16/2020   CYANG44       1. Created this procedure.

   NOTES:

   Automatically available Auto Replace Keywords:
      Object Name:     logger
      Sysdate:         4/16/2020
      Date and Time:   4/16/2020, 3:21:18 PM, and 4/16/2020 3:21:18 PM
      Username:        CYANG44 (set in TOAD Options, Procedure Editor)
      Table Name:       (set in the "New PL/SQL Object" dialog)

******************************************************************************/
BEGIN
    tmpVar := 0;

    IF MESSAGE IS NOT NULL
    THEN
        INSERT INTO z_mid_log (seq,
                               datum,
                               log_type,
                               MESSAGE,
                               pgm,
                               userid)
             VALUES (log_seq.NEXTVAL,
                     SYSDATE,
                     log_type,
                     MESSAGE,
                     pgm,
                     userid);
    END IF;

    COMMIT;
EXCEPTION
    WHEN NO_DATA_FOUND
    THEN
        NULL;
    WHEN OTHERS
    THEN
        ROLLBACK;              -- Consider logging the error and then re-raise
        RAISE;
END logger;
/