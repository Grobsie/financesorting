# FinanceSorting
## Goal
a program which can assign bank statements to categories to get a better overview of spendings

the program would have a few capabilities:
- upload banking details to a mariadb instance (from .csv file)
- auto assign up to two catogories based on a reference list (JSON)
- manually assign tags
- have the ability to add new tags to the reference list

once the data has been categorized the following step would be to make a web app to visualize the data

## checklist
- [X] connect to MariaDB
- [X] create ability to manually add tags
- [X] rewrite tag file to JSON format
- [ ] upload data from .csv file
- [X] create the auto tagging feature
- [ ] create possibility to add new tags
- [ ] create splash menu

