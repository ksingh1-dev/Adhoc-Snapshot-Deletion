# Adhoc-Snapshot-Deletion
1. This project contains a Python script.
2. Also a Jenkins file (Declerative Pipeline)

# Project Details
1. Script deletes EC2 snapshots tagged with 'adhoc=True'
2. Only those snapshots which were created 7 days ago will be deleted.
3. If Snapshots are found first they will deleted and their details will be send in a CSV file attached in an email.
4. If not found then also an Email will send to notify that no snapshots founds that were created 7 days ago.
