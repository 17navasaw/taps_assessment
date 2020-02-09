create database taps_assessment;
USE taps_assessment;
create table Household
(ID int NOT NULL AUTO_INCREMENT,
HousingType varchar(255),
PRIMARY KEY (ID));
create table FamilyMember_test
(ID int NOT NULL AUTO_INCREMENT,
HouseholdId int NOT NULL,
Name varchar(255),
Gender varchar(255),
MaritalStatus varchar(255),
Spouse varchar(255),
OccupationType varchar(255),
AnnualIncome int,
DOB date, PRIMARY KEY (ID),
FOREIGN KEY (HouseholdId) REFERENCES Household(ID))