# Idea is to take a row from the output dataframe where we have a set of
# diagnoses and procedures, and an episode level HRG, and we remove the
# procedure and diagnosis codes one by one and see what the minimum set
# of codes is to still get the same HRG as the original row.

# Hypothisis:
#  A prodecure driven HRG can have all (but one) diagnoses removed and still
#  get the same sub chapter (AANN but _maybe_ not AANNA).

# Hypothgosis:
#  A diagnosis driven HRG can have all procedures removed and still
#  get the same sub chapter (AANN but _maybe_ not AANNA).

# Hypothgosis:
#  A diagnosis driven HRG can have the primary swapped to row 1 if it isn't
#  already and the HRG will not change.

# Hypothgosis:
#  A procedure driven HRG can have the primary swapped to row 1 if it isn't
#  already and the HRG will not change.

# Hypothgosis:
#  For a diagnosis driven HRG, there is at most 20 codes that participate
#  in the HRG calculation. These may not be the first 20 codes in the list, however.

# Hypothgosis:
#  For a procedure driven HRG, there is at most 3 procedure codes that participate
#  in the HRG calculation. These may not be the first 3 codes in the list, however.
#  -- this means just removing the last code and retesting isn't going to be sufficient

# This is basically implemented now in code_drop.py